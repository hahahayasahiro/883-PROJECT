import io,json,sqlite3
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime,timedelta,timezone
import pytest
from fastapi.testclient import TestClient
from pypdf import PdfWriter
from pypdf.generic import NameObject,DictionaryObject,DecodedStreamObject
from test_workflows import client,login,draft
from app import ai
from app.db import connect,initialize,ROOT
from app.main import app


def valid_body(material='My student ID is S1001.'):
    return {'kind':'transcript','fields':{'student_id':'S1001','full_name':'Alex Morgan','email':'student@gcu.example','purpose':'Internship'},'material':material}


def pdf_bytes(text=True,pages=1,encrypted=False):
    w=PdfWriter()
    for _ in range(pages):
        page=w.add_blank_page(612,792)
        if text:
            font=w._add_object(DictionaryObject({NameObject('/Type'):NameObject('/Font'),NameObject('/Subtype'):NameObject('/Type1'),NameObject('/BaseFont'):NameObject('/Helvetica')}))
            page[NameObject('/Resources')]=DictionaryObject({NameObject('/Font'):DictionaryObject({NameObject('/F1'):font})})
            stream=DecodedStreamObject();stream.set_data(b'BT /F1 12 Tf 20 700 Td (Student ID: S1001. Name: Alex Morgan.) Tj ET')
            page[NameObject('/Contents')]=w._add_object(stream)
    if encrypted:w.encrypt('secret')
    out=io.BytesIO();w.write(out);return out.getvalue()


def test_migration_idempotent(client):
    login(client)
    aid=draft(client)
    initialize();initialize()
    with connect() as db:
        assert db.execute('SELECT count(*) FROM schema_versions').fetchone()[0]==1
        assert db.execute('SELECT count(*) FROM application_versions WHERE application_id=?',(aid,)).fetchone()[0]==1
        assert db.execute('SELECT count(*) FROM energy_readings').fetchone()[0]==8*7*6
        assert db.execute('SELECT credits FROM courses LIMIT 1').fetchone()[0]==3


def test_real_old_database_migration(tmp_path,monkeypatch):
    source=ROOT/'data/pre-enhancement-backup.sqlite'
    if not source.exists():pytest.skip('Original local database backup is not distributed.')
    dest=tmp_path/'migrated.sqlite'
    src=sqlite3.connect(source);target=sqlite3.connect(dest);src.backup(target);src.close();target.close()
    monkeypatch.setenv('SMARTCAMPUS_DB',str(dest))
    raw=sqlite3.connect(dest)
    before={table:raw.execute(f'SELECT count(*) FROM {table}').fetchone()[0] for table in ['users','bookings','tickets','applications','reviews']}
    hashes=raw.execute('SELECT id,password_hash FROM users').fetchall();raw.close()
    initialize();initialize()
    with connect() as db:
        for table,n in before.items():assert db.execute(f'SELECT count(*) FROM {table}').fetchone()[0]==n
        assert [tuple(r) for r in db.execute('SELECT id,password_hash FROM users')]==hashes


def test_conversations_followup_isolation(client,monkeypatch):
    login(client);captured=[]
    async def answer(system,prompt,history=None):
        captured.append((prompt,history));return 'CS202 requires CS102 [K02].'
    monkeypatch.setattr(ai,'complete',answer)
    cid=client.post('/api/assistant/conversations').json()['id']
    first=client.post('/api/assistant',json={'question':'CS202 prerequisites','conversation_id':cid})
    assert first.json()['mode']=='live_ai'
    second=client.post('/api/assistant',json={'question':'What does it require?','conversation_id':cid})
    assert any(s['id']=='K02' for s in second.json()['sources'])
    assert len(captured[-1][1])==2
    assert len(client.get(f'/api/assistant/conversations/{cid}').json())==2
    login(client,'student2')
    assert client.get(f'/api/assistant/conversations/{cid}').status_code==404
    assert client.post('/api/assistant',json={'question':'Read this history','conversation_id':cid}).status_code==404


def test_context_capped_at_ten_turns(client,monkeypatch):
    login(client);histories=[]
    async def answer(system,prompt,history=None):histories.append(history);return 'CS202 requires CS102 [K02].'
    monkeypatch.setattr(ai,'complete',answer)
    cid=client.post('/api/assistant/conversations').json()['id']
    for i in range(12):assert client.post('/api/assistant',json={'question':f'CS202 prerequisites question {i}','conversation_id':cid}).status_code==200
    assert len(histories[-1])==20
    assert 'question 0' not in json.dumps(histories[-1])
    assert 'question 1"' in json.dumps(histories[-1])


def test_shortcuts_do_not_act(client):
    login(client)
    result=client.post('/api/assistant',json={'question':'I want to book a room and apply for a transcript'}).json()
    assert {l['page'] for l in result['links']}=={'facilities','reviews'}
    assert client.get('/api/facilities').json()['bookings']==[]


def test_learning_preferences_plan_and_limits(client):
    login(client)
    assert client.put('/api/learning/preferences',json={'interest':'mathematics','goal':'Improve maths'}).status_code==200
    r=client.get('/api/learning').json()
    assert r['recommendations'][0]['area']=='mathematics'
    assert client.post('/api/learning/plan',json={'course_code':'CS301'}).status_code==422
    for code in ['CS102','CS201','CS203','MA101']:assert client.post('/api/learning/plan',json={'course_code':code}).status_code==200
    assert client.post('/api/learning/plan',json={'course_code':'CS102'}).status_code==409
    assert client.post('/api/learning/plan',json={'course_code':'IS201'}).status_code==422
    assert client.get('/api/learning').json()['credits']==12
    login(client,'student2')
    assert client.get('/api/learning').json()['plan']==[]
    assert client.delete('/api/learning/plan/CS102').status_code==404
    login(client);assert client.delete('/api/learning/plan/CS102').status_code==200


def booking_payload(room=1,hour=0):
    start=datetime.now(timezone.utc)+timedelta(days=4,hours=hour)
    return {'room_id':room,'start':start.isoformat(),'end':(start+timedelta(hours=1)).isoformat()}


def test_room_filters_modify_and_alternatives(client):
    login(client);body=booking_payload(3)
    bid=client.post('/api/facilities/bookings',json=body).json()['id']
    r=client.get('/api/facilities',params={'capacity':25,'equipment':'projector','kind':'Laboratory'}).json()
    assert [r['id'] for r in r['rooms']]==[3]
    assert client.put(f'/api/facilities/bookings/{bid}',json=body).status_code==200
    conflict=client.post('/api/facilities/bookings',json=body)
    assert conflict.status_code==409
    assert all(x['id']!=3 for x in conflict.json()['detail']['alternatives'])
    filtered=client.get('/api/facilities',params={'start':body['start'],'end':body['end']}).json()
    assert 3 not in [r['id'] for r in filtered['rooms']]
    other=client.post('/api/facilities/bookings',json=booking_payload(4)).json()['id']
    assert client.put(f'/api/facilities/bookings/{other}',json=body).status_code==409
    assert next(b for b in client.get('/api/facilities').json()['bookings'] if b['id']==other)['room_id']==4
    assert client.request('DELETE',f'/api/facilities/bookings/{bid}',json={'reason':'Meeting cancelled'}).status_code==200
    assert any(b['cancel_reason']=='Meeting cancelled' for b in client.get('/api/facilities').json()['bookings'])


def test_concurrent_booking_modifications(client):
    login(client);cookie=dict(client.cookies)
    a=client.post('/api/facilities/bookings',json=booking_payload(1)).json()['id']
    b=client.post('/api/facilities/bookings',json=booking_payload(2)).json()['id']
    def move(bid):
        with TestClient(app,cookies=cookie) as c:return c.put(f'/api/facilities/bookings/{bid}',json=booking_payload(3,2)).status_code
    with ThreadPoolExecutor(max_workers=2) as pool:assert sorted(pool.map(move,[a,b]))==[200,409]


def test_maintenance_history_cost_and_energy(client,monkeypatch):
    login(client)
    async def classified(system,data,model):return model.model_validate({'category':'it','priority':'high','reason':'Projector failure'})
    monkeypatch.setattr(ai,'structured',classified)
    assert client.post('/api/maintenance/classify',json={'description':'Projector fails'}).json()['mode']=='live_ai'
    tid=client.post('/api/facilities/faults',json={'room_id':3,'description':'Projector fails','category':'it','priority':'high'}).json()['id']
    assert client.post(f'/api/maintenance/tickets/{tid}/logs',json={'note':'Unauthorized'}).status_code==403
    login(client,'maintenance')
    assert client.patch(f'/api/maintenance/tickets/{tid}',json={'status':'in_progress','eta':(datetime.now(timezone.utc)+timedelta(days=1)).isoformat(),'note':'Investigating'}).status_code==200
    assert client.post(f'/api/maintenance/tickets/{tid}/logs',json={'note':'Replaced cable','cost':35}).status_code==200
    assert client.patch(f'/api/maintenance/tickets/{tid}',json={'status':'completed','note':'Checked display'}).status_code==200
    logs=client.get(f'/api/maintenance/tickets/{tid}/logs').json()
    assert len(logs)==4 and sum(x['cost'] for x in logs)==35
    r=client.get('/api/maintenance',params={'room_id':3,'priority':'high'}).json()
    assert r['tickets'][0]['cost']==35
    energy=client.get('/api/maintenance',params={'room_id':3,'day':r['days'][0]}).json()['energy']
    assert energy==client.get('/api/maintenance',params={'room_id':3,'day':r['days'][0]}).json()['energy']
    assert energy!=client.get('/api/maintenance',params={'room_id':3,'day':r['days'][1]}).json()['energy']
    login(client,'student2');assert client.get(f'/api/maintenance/tickets/{tid}/logs').status_code==404


@pytest.mark.parametrize('name,data,status',[('record.txt',b'Student ID: S1001',200),('record.pdf',pdf_bytes(),200),('scan.pdf',pdf_bytes(False),422),('large.pdf',pdf_bytes(pages=21),422),('secret.pdf',pdf_bytes(encrypted=True),422),('fake.pdf',b'fake',422),('binary.exe',b'hello',422),('empty.txt',b'',422),('big.txt',b'x'*(5*1024*1024+1),413),('bad.txt',b'\x00\x01',422)])
def test_upload_boundaries(client,name,data,status):
    login(client)
    response=client.post('/api/reviews/upload',files={'file':(name,data)})
    assert response.status_code==status
    if status==200:assert 'S1001' in response.json()['text']


def test_extract_requires_evidence_and_does_not_modify(client,monkeypatch):
    login(client);aid=draft(client)
    async def candidates(system,data,model):return model.model_validate({'candidates':[{'field':'student_id','value':'S1001','evidence':'Student ID: S1001'},{'field':'full_name','value':'Invented Name','evidence':'not in text'}]})
    monkeypatch.setattr(ai,'structured',candidates)
    result=client.post('/api/reviews/extract',json={'text':'Student ID: S1001'}).json()
    assert len(result['candidates'])==1
    assert client.get('/api/applications').json()['applications'][0]['version']==1


def test_versioned_return_and_notifications(client):
    login(client);aid=draft(client)
    assert client.post('/api/reviews',json={'application_id':aid}).status_code==200
    assert client.post(f'/api/applications/{aid}/submit').status_code==200
    login(client,'admin')
    assert client.patch(f'/api/applications/{aid}/decision',json={'status':'returned','note':'Correct the student ID in your material.'}).status_code==200
    login(client)
    assert client.post(f'/api/applications/{aid}/submit').status_code==409
    assert client.put(f'/api/applications/{aid}',json=valid_body()).json()['version']==2
    unchanged=valid_body();unchanged['fields']['certificate_type']=''
    assert client.put(f'/api/applications/{aid}',json=unchanged).json()['version']==2
    assert client.put(f'/api/applications/{aid}',json=valid_body()).json()['version']==2
    assert client.get(f'/api/reviews/{aid}').json()[0]['stale'] is True
    versions=client.get(f'/api/reviews/{aid}/versions').json()
    assert any(c['field']=='material' for c in versions[-1]['changes'])
    assert client.post('/api/reviews',json={'application_id':aid}).json()['version']==2
    assert client.post(f'/api/applications/{aid}/submit').status_code==200
    notifications=client.get('/api/applications/notifications').json()
    assert any('returned' in n['message'] for n in notifications)
    nid=notifications[0]['id']
    login(client,'student2')
    assert client.post(f'/api/applications/notifications/{nid}/read').status_code==404
    assert client.get(f'/api/reviews/{aid}/versions').status_code==404
    assert client.get(f'/api/applications/{aid}/timeline').status_code==404
    login(client,'admin')
    assert client.patch(f'/api/applications/{aid}/decision',json={'status':'approved','note':'Corrections verified'}).status_code==200
    login(client)
    actions=[e['action'] for e in client.get(f'/api/applications/{aid}/timeline').json()]
    assert actions==['draft_created','submitted','returned','revised','resubmitted','approved']
    assert client.post(f'/api/applications/notifications/{nid}/read').status_code==200
    assert client.get('/api/applications',params={'status':'approved','q':str(aid)}).json()['applications'][0]['id']==aid


def test_invalid_structured_ai_and_stale_review(client,monkeypatch):
    login(client);aid=draft(client)
    async def bad(*args):return 'not json'
    monkeypatch.setattr(ai,'complete',bad)
    assert client.post('/api/maintenance/classify',json={'description':'Broken projector'}).json()['mode']=='manual'
    assert client.post('/api/reviews',json={'application_id':aid}).json()['mode']=='rules_only'
    async def racing(system,data,model):
        with connect() as db:db.execute('UPDATE applications SET version=version+1 WHERE id=?',(aid,))
        return None
    monkeypatch.setattr(ai,'structured',racing)
    assert client.post('/api/reviews',json={'application_id':aid}).status_code==409
