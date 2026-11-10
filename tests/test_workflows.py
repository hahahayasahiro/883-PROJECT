import importlib
from datetime import datetime,timedelta,timezone
from concurrent.futures import ThreadPoolExecutor
import httpx
import pytest
from fastapi.testclient import TestClient
from app import ai
from app.db import initialize,connect
from app.main import app


@pytest.fixture
def client(tmp_path,monkeypatch):
    monkeypatch.setenv('SMARTCAMPUS_DB',str(tmp_path/'test.sqlite'))
    monkeypatch.delenv('DEEPSEEK_API_KEY',raising=False)
    with TestClient(app) as c:
        yield c


def login(c,name='student'):
    r=c.post('/api/auth/login',json={'username':name,'password':'Campus2026!'})
    assert r.status_code==200


def draft(c,**updates):
    fields={'student_id':'S1001','full_name':'Alex Morgan','email':'student@gcu.example','purpose':'Internship'}
    fields.update(updates)
    return c.post('/api/applications',json={'kind':'transcript','fields':fields,'material':'My student ID is S9999.'}).json()['id']


def test_auth_and_static(client):
    assert client.get('/').status_code==200
    assert client.get('/api/learning').status_code==401
    assert client.post('/api/auth/login',json={'username':'student','password':'wrong'}).status_code==401
    login(client)
    assert client.get('/api/auth/me').json()['student_id']=='S1001'
    assert client.post('/api/auth/logout').status_code==200
    assert client.get('/api/auth/me').status_code==401


def test_learning_and_evidence(client):
    login(client)
    learning=client.get('/api/learning').json()
    assert any(x['course']=='MA101' for x in learning['risks'])
    assert all(x['code']!='CS301' for x in learning['recommendations'])
    assert len(learning['records'])==3
    result=client.post('/api/assistant',json={'question':'What are the prerequisites for CS202?'}).json()
    assert result['mode']=='retrieval_only'
    assert any(s['id']=='K02' for s in result['sources'])
    assert client.post('/api/assistant',json={'question':'Who won the football world cup?'}).json()['mode']=='no_evidence'


def test_booking_conflict_and_ownership(client):
    login(client)
    start=datetime.now(timezone.utc)+timedelta(days=2)
    payload={'room_id':1,'start':start.isoformat(),'end':(start+timedelta(hours=1)).isoformat()}
    r=client.post('/api/facilities/bookings',json=payload)
    assert r.status_code==200
    bid=r.json()['id']
    assert client.post('/api/facilities/bookings',json=payload).status_code==409
    login(client,'student2')
    assert client.delete(f'/api/facilities/bookings/{bid}').status_code==404
    login(client)
    assert client.delete(f'/api/facilities/bookings/{bid}').status_code==200
    assert client.post('/api/facilities/bookings',json=payload).status_code==200
    payload['end']=(start+timedelta(hours=3)).isoformat()
    assert client.post('/api/facilities/bookings',json=payload).status_code==422


def test_fault_to_maintenance(client):
    login(client)
    tid=client.post('/api/facilities/faults',json={'room_id':2,'description':'Broken air conditioning'}).json()['id']
    assert client.patch(f'/api/maintenance/tickets/{tid}',json={'status':'in_progress'}).status_code==403
    login(client,'maintenance')
    assert any(t['id']==tid for t in client.get('/api/maintenance').json()['tickets'])
    assert client.patch(f'/api/maintenance/tickets/{tid}',json={'status':'completed'}).status_code==409
    assert client.patch(f'/api/maintenance/tickets/{tid}',json={'status':'in_progress'}).status_code==200
    assert client.patch(f'/api/maintenance/tickets/{tid}',json={'status':'completed','cost':45}).status_code==200
    assert client.get('/api/maintenance').json()['total_cost']==45


def test_application_review_to_decision(client):
    login(client)
    aid=draft(client,purpose='')
    review=client.post('/api/reviews',json={'application_id':aid}).json()
    assert review['mode']=='rules_only'
    assert len(review['issues'])>=2
    assert client.post(f'/api/applications/{aid}/submit').status_code==422
    assert client.patch(f'/api/applications/{aid}/decision',json={'status':'approved','note':'OK to issue'}).status_code==403
    login(client,'student2')
    assert client.get(f'/api/reviews/{aid}').status_code==404
    assert client.post(f'/api/applications/{aid}/submit').status_code==404
    login(client)
    payload={'kind':'transcript','fields':{'student_id':'S1001','full_name':'Alex Morgan','email':'student@gcu.example','purpose':'Internship'},'material':'My student ID is S1001.'}
    assert client.put(f'/api/applications/{aid}',json=payload).status_code==200
    assert client.get(f'/api/reviews/{aid}').json()[0]['stale'] is True
    assert client.post('/api/reviews',json={'application_id':aid}).json()['issues']==[]
    assert client.post(f'/api/applications/{aid}/submit').status_code==200
    login(client,'admin')
    assert client.patch(f'/api/applications/{aid}/decision',json={'status':'approved','note':'Verified demonstration details'}).status_code==200
    login(client)
    found=next(a for a in client.get('/api/applications').json()['applications'] if a['id']==aid)
    assert found['status']=='approved'
    assert client.put(f'/api/applications/{aid}',json=payload).status_code==409


def test_ai_success_and_no_citation(client,monkeypatch):
    async def answer(*args):return 'CS202 requires CS102 [K02].'
    monkeypatch.setattr(ai,'complete',answer)
    login(client)
    assert client.post('/api/assistant',json={'question':'CS202 prerequisites'}).json()['mode']=='live_ai'
    async def bad(*args):return 'Unsupported answer without citations.'
    monkeypatch.setattr(ai,'complete',bad)
    assert client.post('/api/assistant',json={'question':'CS202 prerequisites'}).json()['mode']=='retrieval_only'
    async def review(system,data,model):return model.model_validate({'summary':'The text has a different ID.','checks':[{'label':'ID mismatch','status':'fail','evidence':'S9999','suggestion':'Use S1001.'}]})
    monkeypatch.setattr(ai,'structured',review)
    assert client.post('/api/reviews',json={'application_id':draft(client)}).json()['mode']=='live_ai'


@pytest.mark.parametrize('failure',['timeout','unauthorized','malformed','success'])
def test_actual_ai_adapter(client,monkeypatch,failure):
    import asyncio
    monkeypatch.setenv('DEEPSEEK_API_KEY','test-placeholder')
    async def handler(request):
        assert request.headers['authorization']=='Bearer test-placeholder'
        if failure=='timeout':raise httpx.ReadTimeout('simulated')
        if failure=='unauthorized':return httpx.Response(401,json={'error':'no'})
        if failure=='malformed':return httpx.Response(200,json={'unexpected':True})
        return httpx.Response(200,json={'choices':[{'message':{'content':'Response'}}]})
    original=httpx.AsyncClient
    monkeypatch.setattr(ai.httpx,'AsyncClient',lambda **kwargs:original(transport=httpx.MockTransport(handler),**kwargs))
    assert asyncio.run(ai.complete('system','question'))==('Response' if failure=='success' else None)


def test_persistence_seed_and_origin(client):
    login(client)
    aid=draft(client)
    initialize()
    with connect() as db:
        assert db.execute('SELECT count(*) FROM courses').fetchone()[0]==10
        assert db.execute('SELECT count(*) FROM knowledge').fetchone()[0]==15
        assert db.execute('SELECT id FROM applications WHERE id=?',(aid,)).fetchone()
    assert client.post('/api/auth/logout',headers={'Origin':'https://other.example'}).status_code==403


def test_atomic_conflicts(client):
    login(client)
    cookies=dict(client.cookies)
    start=datetime.now(timezone.utc)+timedelta(days=3)
    body={'room_id':4,'start':start.isoformat(),'end':(start+timedelta(hours=1)).isoformat()}
    def reserve(_):
        with TestClient(app,cookies=cookies) as c:return c.post('/api/facilities/bookings',json=body).status_code
    with ThreadPoolExecutor(max_workers=2) as pool:
        assert sorted(pool.map(reserve,range(2)))==[200,409]
