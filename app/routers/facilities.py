import json
from datetime import datetime,timezone,date,timedelta
from fastapi import APIRouter,Depends,HTTPException,Query
from pydantic import BaseModel,Field
from typing import Literal
from ..auth import roles
from ..db import connect,rows

router=APIRouter(prefix='/api/facilities',tags=['M2.1 Facilities'])
class Booking(BaseModel):
    room_id:int
    start:datetime
    end:datetime
class Cancel(BaseModel):
    reason:str=Field(default='Plans changed',min_length=3,max_length=500)
class Fault(BaseModel):
    room_id:int
    description:str=Field(min_length=5,max_length=2000)
    category:Literal['electrical','hvac','it','plumbing','other']='other'
    priority:Literal['low','normal','high']='normal'

def utc(t):
    return t.replace(tzinfo=timezone.utc) if t.tzinfo is None else t.astimezone(timezone.utc)

def interval(start,end):
    s,e=utc(start),utc(end)
    if s<=datetime.now(timezone.utc) or not 0<(e-s).total_seconds()<=7200:raise HTTPException(422,'Choose a future slot of up to two hours.')
    return s.isoformat(),e.isoformat()

def available(db,room_id,s,e,exclude=0):
    return not db.execute("SELECT id FROM bookings WHERE room_id=? AND status='active' AND start<? AND end>? AND id!=?",(room_id,e,s,exclude)).fetchone()

@router.get('')
def facilities(day:date|None=None,start:datetime|None=None,end:datetime|None=None,capacity:int=Query(default=1,ge=1,le=1000),kind:str='',equipment:str='',user=Depends(roles('student','admin','maintenance'))):
    if (start is None)!=(end is None):raise HTTPException(422,'Provide both start and end.')
    if start and utc(end)<=utc(start):raise HTTPException(422,'End must follow start.')
    room_list=rows('SELECT * FROM rooms WHERE capacity>=? AND (? = ? OR kind=?)',(capacity,kind,'',kind))
    for r in room_list:r['equipment']=json.loads(r['equipment'])
    if equipment:room_list=[r for r in room_list if equipment.lower() in r['equipment']]
    with connect() as db:
        if start:room_list=[r for r in room_list if available(db,r['id'],utc(start).isoformat(),utc(end).isoformat())]
    bookings=rows('SELECT bookings.*,rooms.name AS room FROM bookings JOIN rooms ON rooms.id=room_id WHERE user_id=? ORDER BY start DESC',(user['id'],))
    slots=rows("SELECT room_id,start,end FROM bookings WHERE status='active' ORDER BY start")
    if day:
        d0=datetime.combine(day,datetime.min.time(),tzinfo=timezone.utc)
        slots=[b for b in slots if b['start']<(d0+timedelta(days=1)).isoformat() and b['end']>d0.isoformat()]
    return {'rooms':room_list,'bookings':bookings,'availability':slots,'all_rooms':[{**r,'equipment':json.loads(r['equipment'])} for r in rows('SELECT * FROM rooms')],'day_basis':'UTC date for the daily timetable'}

def save_booking(body,user,bid=None):
    s,e=interval(body.start,body.end)
    with connect() as db:
        db.execute('BEGIN IMMEDIATE')
        if bid:
            old=db.execute("SELECT * FROM bookings WHERE id=? AND user_id=? AND status='active'",(bid,user['id'])).fetchone()
            if not old:raise HTTPException(404,'Active booking not found.')
        if not db.execute('SELECT id FROM rooms WHERE id=?',(body.room_id,)).fetchone():raise HTTPException(404,'Room not found.')
        if not available(db,body.room_id,s,e,bid or 0):
            alternatives=[dict(r) for r in db.execute('SELECT id,name,capacity FROM rooms') if available(db,r['id'],s,e)]
            raise HTTPException(409,{'message':'This slot conflicts with an active booking. Choose an available alternative.','alternatives':alternatives})
        if bid:db.execute('UPDATE bookings SET room_id=?,start=?,end=? WHERE id=?',(body.room_id,s,e,bid))
        else:bid=db.execute("INSERT INTO bookings(user_id,room_id,start,end,created) VALUES(?,?,?,?,CURRENT_TIMESTAMP)",(user['id'],body.room_id,s,e)).lastrowid
    return {'id':bid,'status':'active'}

@router.post('/bookings')
def book(body:Booking,user=Depends(roles('student'))):return save_booking(body,user)
@router.put('/bookings/{bid}')
def edit(bid:int,body:Booking,user=Depends(roles('student'))):return save_booking(body,user,bid)

@router.delete('/bookings/{bid}')
def cancel(bid:int,body:Cancel|None=None,user=Depends(roles('student'))):
    reason=body.reason if body else 'Plans changed'
    with connect() as db:
        cur=db.execute("UPDATE bookings SET status='cancelled',cancel_reason=? WHERE id=? AND user_id=? AND status='active'",(reason,bid,user['id']))
        if not cur.rowcount:raise HTTPException(404,'Active booking not found.')
    return {'status':'cancelled'}

@router.post('/faults')
def fault(body:Fault,user=Depends(roles('student'))):
    with connect() as db:
        if not db.execute('SELECT id FROM rooms WHERE id=?',(body.room_id,)).fetchone():raise HTTPException(404,'Room not found.')
        tid=db.execute('INSERT INTO tickets(user_id,room_id,description,category,priority) VALUES(?,?,?,?,?)',(user['id'],body.room_id,body.description,body.category,body.priority)).lastrowid
        db.execute("INSERT INTO ticket_logs(ticket_id,actor_id,note,status) VALUES(?,?,?,'open')",(tid,user['id'],'Fault reported'))
    return {'id':tid,'status':'open'}
