import json
from typing import Literal
from fastapi import APIRouter,Depends,HTTPException,Query
from pydantic import BaseModel,Field
from ..auth import roles
from ..db import connect,rows

router=APIRouter(prefix='/api/applications',tags=['M3.2 Applications'])
class Application(BaseModel):
    kind:Literal['transcript','certificate']
    fields:dict[str,str]
    material:str=Field(default='',max_length=60000)
    file_name:str=Field(default='',max_length=250)
class Decision(BaseModel):
    status:Literal['approved','rejected','returned']
    note:str=Field(min_length=3,max_length=1000)

def owned(db,aid,user,staff=False):
    row=db.execute('SELECT * FROM applications WHERE id=?',(aid,)).fetchone()
    if not row or (not (staff and user['role']=='admin') and row['user_id']!=user['id']):raise HTTPException(404,'Application not found.')
    return row

def check(fields,kind,user):
    required=['student_id','full_name','email','purpose']+(['certificate_type'] if kind=='certificate' else [])
    issues=[f'Missing {key.replace("_"," ")}' for key in required if not fields.get(key,'').strip()]
    for key,expected in [('student_id',user['student_id']),('full_name',user['name']),('email',user['email'])]:
        if fields.get(key,'').strip().casefold()!=expected.casefold():issues.append(key.replace('_',' ').title()+' must match the signed-in student.')
    return issues

def validate(body):
    if len(body.fields)>12 or any(len(k)>80 or len(v)>2000 for k,v in body.fields.items()):raise HTTPException(422,'Application fields are too long.')

def snapshot(db,aid):
    a=db.execute('SELECT * FROM applications WHERE id=?',(aid,)).fetchone()
    db.execute('INSERT INTO application_versions(application_id,version,kind,fields,material,file_name) VALUES(?,?,?,?,?,?)',(aid,a['version'],a['kind'],a['fields'],a['material'],a['file_name']))

def event(db,aid,actor,action,note,version):
    db.execute('INSERT INTO application_events(application_id,actor_id,action,note,version) VALUES(?,?,?,?,?)',(aid,actor,action,note,version))

def notify(db,uid,aid,message):
    db.execute('INSERT INTO notifications(user_id,application_id,message) VALUES(?,?,?)',(uid,aid,message))

@router.get('')
def listing(q:str=Query(default='',max_length=200),status:str='',kind:str='',user=Depends(roles('student','admin'))):
    items=rows('SELECT applications.*,users.name AS applicant FROM applications JOIN users ON users.id=user_id'+(' WHERE user_id=?' if user['role']=='student' else '')+' ORDER BY applications.id DESC',(user['id'],) if user['role']=='student' else ())
    counts={s:sum(a['status']==s for a in items) for s in ['draft','submitted','returned','approved','rejected']}
    durations=rows("SELECT (julianday(decided_at)-julianday(submitted_at))*24 AS hours FROM applications WHERE decided_at!='' AND submitted_at!=''"+(' AND user_id=?' if user['role']=='student' else ''),(user['id'],) if user['role']=='student' else ())
    hours=[r['hours'] for r in durations if r['hours'] is not None and r['hours']>=0]
    if status:items=[a for a in items if a['status']==status]
    if kind:items=[a for a in items if a['kind']==kind]
    if q:items=[a for a in items if q.casefold() in (str(a['id'])+' '+a['applicant']+' '+a['fields']).casefold()]
    for a in items:a['fields']=json.loads(a['fields'])
    return {'applications':items,'counts':counts,'pending':counts['submitted'],'average_processing_hours':round(sum(hours)/len(hours),3) if hours else None,'unread':rows('SELECT count(*) AS n FROM notifications WHERE user_id=? AND is_read=0',(user['id'],))[0]['n']}

@router.get('/notifications')
def notifications(user=Depends(roles('student','admin'))):
    return rows('SELECT * FROM notifications WHERE user_id=? ORDER BY id DESC LIMIT 100',(user['id'],))

@router.post('/notifications/{nid}/read')
def read_notification(nid:int,user=Depends(roles('student','admin'))):
    with connect() as db:
        if not db.execute('UPDATE notifications SET is_read=1 WHERE id=? AND user_id=?',(nid,user['id'])).rowcount:raise HTTPException(404,'Notification not found.')
    return {'ok':True}

@router.post('')
def create(body:Application,user=Depends(roles('student'))):
    validate(body)
    with connect() as db:
        aid=db.execute("INSERT INTO applications(user_id,kind,fields,material,file_name,created) VALUES(?,?,?,?,?,CURRENT_TIMESTAMP)",(user['id'],body.kind,json.dumps(body.fields),body.material,body.file_name)).lastrowid
        snapshot(db,aid);event(db,aid,user['id'],'draft_created','Draft created',1)
    return {'id':aid,'status':'draft','version':1}

@router.put('/{aid}')
def edit(aid:int,body:Application,user=Depends(roles('student'))):
    validate(body)
    with connect() as db:
        db.execute('BEGIN IMMEDIATE')
        item=owned(db,aid,user)
        if item['status'] not in ['draft','returned']:raise HTTPException(409,'Only drafts or returned applications can be edited.')
        previous_fields={k:v for k,v in json.loads(item['fields']).items() if v!=''}
        next_fields={k:v for k,v in body.fields.items() if v!=''}
        changed=item['kind']!=body.kind or previous_fields!=next_fields or item['material']!=body.material or item['file_name']!=body.file_name or item['status']=='returned'
        version=item['version']+int(changed)
        if changed:
            db.execute("UPDATE applications SET kind=?,fields=?,material=?,file_name=?,version=?,status='draft' WHERE id=?",(body.kind,json.dumps(body.fields),body.material,body.file_name,version,aid))
            snapshot(db,aid);event(db,aid,user['id'],'revised','Saved revised application',version)
    return {'id':aid,'status':'draft','version':version}

@router.post('/{aid}/submit')
def submit(aid:int,user=Depends(roles('student'))):
    with connect() as db:
        db.execute('BEGIN IMMEDIATE')
        item=owned(db,aid,user)
        if item['status']!='draft':raise HTTPException(409,'Save a draft revision before submitting.')
        issues=check(json.loads(item['fields']),item['kind'],user)
        if issues:raise HTTPException(422,'; '.join(issues))
        action='resubmitted' if item['was_returned'] else 'submitted'
        db.execute("UPDATE applications SET status='submitted',submitted_at=CURRENT_TIMESTAMP,decided_at='' WHERE id=?",(aid,))
        event(db,aid,user['id'],action,'Sent to administrative staff',item['version'])
        for admin in db.execute("SELECT id FROM users WHERE role='admin'").fetchall():notify(db,admin['id'],aid,f'Application #{aid} {action} by {user["name"]}.')
        notify(db,user['id'],aid,f'Application #{aid} {action}.')
    return {'id':aid,'status':'submitted'}

@router.patch('/{aid}/decision')
def decide(aid:int,body:Decision,user=Depends(roles('admin'))):
    if len(body.note.strip())<3:raise HTTPException(422,'Explain your decision.')
    with connect() as db:
        db.execute('BEGIN IMMEDIATE')
        item=owned(db,aid,user,staff=True)
        if item['status']!='submitted':raise HTTPException(409,'Application must be submitted before a decision.')
        db.execute("UPDATE applications SET status=?,decision_note=?,was_returned=?,decided_at=CASE WHEN ?='returned' THEN '' ELSE CURRENT_TIMESTAMP END WHERE id=?",(body.status,body.note,int(body.status=='returned' or item['was_returned']),body.status,aid))
        event(db,aid,user['id'],body.status,body.note,item['version'])
        notify(db,item['user_id'],aid,f'Application #{aid} {body.status}: {body.note}')
    return {'id':aid,'status':body.status}

@router.get('/{aid}/timeline')
def timeline(aid:int,user=Depends(roles('student','admin'))):
    with connect() as db:owned(db,aid,user,staff=True)
    return rows('SELECT application_events.*,users.name AS actor FROM application_events JOIN users ON users.id=actor_id WHERE application_id=? ORDER BY application_events.id',(aid,))
