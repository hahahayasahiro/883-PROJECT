from datetime import date,datetime,timezone
from typing import Literal
from fastapi import APIRouter,Depends,HTTPException,Query
from pydantic import BaseModel,Field,ConfigDict
from ..auth import roles
from ..db import connect,rows
from .. import ai

router=APIRouter(prefix='/api/maintenance',tags=['M2.2 Maintenance'])
Category=Literal['electrical','hvac','it','plumbing','other']
Priority=Literal['low','normal','high']

class Classification(BaseModel):
    model_config=ConfigDict(extra='forbid')
    category:Category
    priority:Priority
    reason:str=Field(min_length=1,max_length=500)
class Description(BaseModel):
    description:str=Field(min_length=5,max_length=2000)
class Update(BaseModel):
    status:Literal['open','in_progress','completed']|None=None
    cost:float|None=Field(default=None,ge=0,le=100000,allow_inf_nan=False)
    category:Category|None=None
    priority:Priority|None=None
    eta:datetime|None=None
    note:str=Field(default='',max_length=2000)
class Log(BaseModel):
    note:str=Field(min_length=3,max_length=2000)
    cost:float=Field(default=0,ge=0,le=100000,allow_inf_nan=False)

@router.post('/classify')
async def classify(body:Description,user=Depends(roles('student','maintenance'))):
    result=await ai.structured('Suggest a maintenance category and priority, with a short reason. category must be electrical,hvac,it,plumbing,other; priority must be low,normal,high. These are advisory suggestions requiring human confirmation.',{'description':body.description},Classification)
    return {'mode':'live_ai' if result else 'manual','suggestion':result.model_dump() if result else None,'notice':'Confirm suggestions before saving. If AI is unavailable, choose the category manually.'}

@router.get('')
def overview(status:str='',priority:str='',room_id:int|None=None,day:date|None=None,user=Depends(roles('student','maintenance','admin'))):
    tickets=rows('SELECT tickets.*,rooms.name AS room FROM tickets JOIN rooms ON rooms.id=room_id'+(' WHERE user_id=?' if user['role']=='student' else ''),(user['id'],) if user['role']=='student' else ())
    if status:tickets=[t for t in tickets if t['status']==status]
    if priority:tickets=[t for t in tickets if t['priority']==priority]
    if room_id:tickets=[t for t in tickets if t['room_id']==room_id]
    days=[r['day'] for r in rows('SELECT DISTINCT day FROM energy_readings ORDER BY day DESC')]
    selected=day.isoformat() if day else days[0] if days else date.today().isoformat()
    energy=rows('SELECT hour,round(sum(kwh),2) AS kwh,round(avg(occupancy)) AS occupancy FROM energy_readings WHERE day=?'+(' AND room_id=?' if room_id else '')+' GROUP BY hour ORDER BY hour',(selected,room_id) if room_id else (selected,))
    return {'tickets':tickets,'energy':energy,'day':selected,'days':days,'rooms':rows('SELECT id,name FROM rooms'),'energy_mode':'Persisted synthetic readings only. No real equipment control.','total_cost':sum(t['cost'] for t in tickets)}

def ticket(db,tid,user):
    row=db.execute('SELECT * FROM tickets WHERE id=?',(tid,)).fetchone()
    if not row or (user['role']=='student' and row['user_id']!=user['id']):raise HTTPException(404,'Ticket not found.')
    return row

@router.get('/tickets/{tid}/logs')
def logs(tid:int,user=Depends(roles('student','maintenance','admin'))):
    with connect() as db:ticket(db,tid,user)
    return rows('SELECT ticket_logs.*,users.name AS actor FROM ticket_logs JOIN users ON users.id=actor_id WHERE ticket_id=? ORDER BY ticket_logs.id',(tid,))

@router.post('/tickets/{tid}/logs')
def add_log(tid:int,body:Log,user=Depends(roles('maintenance'))):
    with connect() as db:
        db.execute('BEGIN IMMEDIATE')
        item=ticket(db,tid,user)
        if item['status']=='completed':raise HTTPException(409,'Completed tickets are read-only.')
        db.execute('INSERT INTO ticket_logs(ticket_id,actor_id,note,status,cost) VALUES(?,?,?,?,?)',(tid,user['id'],body.note,item['status'],body.cost))
        db.execute('UPDATE tickets SET cost=cost+? WHERE id=?',(body.cost,tid))
    return {'ok':True}

@router.patch('/tickets/{tid}')
def update(tid:int,body:Update,user=Depends(roles('maintenance'))):
    with connect() as db:
        db.execute('BEGIN IMMEDIATE')
        item=ticket(db,tid,user)
        if item['status']=='completed':raise HTTPException(409,'Completed tickets are read-only.')
        status=body.status or item['status']
        if status!=item['status'] and {'open':'in_progress','in_progress':'completed'}.get(item['status'])!=status:raise HTTPException(409,'Move open work to in_progress, then completed.')
        eta=body.eta.astimezone(timezone.utc).isoformat() if body.eta and body.eta.tzinfo else body.eta.replace(tzinfo=timezone.utc).isoformat() if body.eta else item['eta']
        cost=item['cost'] if body.cost is None else body.cost
        db.execute('UPDATE tickets SET status=?,cost=?,category=?,priority=?,eta=? WHERE id=?',(status,cost,body.category or item['category'],body.priority or item['priority'],eta,tid))
        db.execute('INSERT INTO ticket_logs(ticket_id,actor_id,note,status,cost) VALUES(?,?,?,?,?)',(tid,user['id'],body.note or 'Ticket details updated',status,cost-item['cost']))
    return {'id':tid,'status':status}
