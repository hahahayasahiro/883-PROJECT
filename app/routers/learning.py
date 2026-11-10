from typing import Literal
from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field
from ..auth import roles
from ..db import rows,connect
router=APIRouter(prefix='/api/learning',tags=['M1.2 Learning'])

class Preferences(BaseModel):
    interest: Literal['computing','ai','mathematics','management']='computing'
    goal: str=Field(default='',max_length=500)
class PlanCourse(BaseModel):
    term: str=Field(default='2027 Semester 1',min_length=3,max_length=60)
    course_code: str=Field(max_length=20)

def eligible(db,user,code):
    course=db.execute('SELECT * FROM courses WHERE code=?',(code,)).fetchone()
    if not course:raise HTTPException(404,'Course not found.')
    passed={r[0] for r in db.execute('SELECT course_code FROM records WHERE user_id=? AND grade>=50',(user['id'],))}
    if code in passed:raise HTTPException(422,'You have already passed this course.')
    if course['prerequisite'] and course['prerequisite'] not in passed:raise HTTPException(422,'Pass the prerequisite first: '+course['prerequisite'])
    return course

@router.get('')
def learning(term:str=Query(default='2027 Semester 1',min_length=3,max_length=60),user=Depends(roles('student'))):
    records=rows('SELECT records.*,courses.name FROM records JOIN courses ON code=course_code WHERE user_id=?',(user['id'],))
    pref=rows('SELECT interest,goal FROM learning_preferences WHERE user_id=?',(user['id'],))
    pref=pref[0] if pref else {'interest':'computing','goal':''}
    passed={r['course_code'] for r in records if r['grade']>=50}
    courses=rows('SELECT * FROM courses')
    recommendations=[dict(c,score=(2 if c['area']==pref['interest'] else 0)+(1 if c['prerequisite'] else 0),reason=('Matches your interest. ' if c['area']==pref['interest'] else '')+('Prerequisite passed: '+c['prerequisite'] if c['prerequisite'] else 'No prerequisite required')) for c in courses if c['code'] not in passed and (not c['prerequisite'] or c['prerequisite'] in passed)]
    recommendations.sort(key=lambda c:(-c['score'],c['code']))
    if pref['interest']=='ai':
        for c in recommendations:
            if c['code'] in ['CS102','MA101','ST201']:
                c['score']+=2
                c['reason']='Builds foundations for your AI interest. '+c['reason']
        recommendations.sort(key=lambda c:(-c['score'],c['code']))
    risks=[]
    for r in records:
        reasons=[]
        if r['grade']<50:reasons.append(f"Mark {r['grade']:g} is below 50")
        if r['attendance']<75:reasons.append(f"Attendance {r['attendance']:g}% is below 75%")
        if reasons:risks.append({'course':r['course_code'],'reason':'; '.join(reasons),'action':'Book a tutor appointment, review missed topics, and schedule two study sessions this week.'})
    plan=rows('SELECT courses.* FROM learning_plans JOIN courses ON code=course_code WHERE user_id=? AND term=? ORDER BY code',(user['id'],term))
    return {'records':records,'courses':courses,'recommendations':recommendations,'risks':risks,'preferences':pref,'plan':plan,'term':term,'credits':sum(c['credits'] for c in plan),'credit_limit':12,'mode':'Rule-based demonstration. The 12-credit term limit is synthetic; no trained risk model.'}

@router.put('/preferences')
def preferences(body:Preferences,user=Depends(roles('student'))):
    with connect() as db:db.execute('INSERT INTO learning_preferences VALUES(?,?,?) ON CONFLICT(user_id) DO UPDATE SET interest=excluded.interest,goal=excluded.goal',(user['id'],body.interest,body.goal))
    return body.model_dump()

@router.post('/plan')
def add(body:PlanCourse,user=Depends(roles('student'))):
    with connect() as db:
        db.execute('BEGIN IMMEDIATE')
        course=eligible(db,user,body.course_code)
        if db.execute('SELECT 1 FROM learning_plans WHERE user_id=? AND term=? AND course_code=?',(user['id'],body.term,body.course_code)).fetchone():raise HTTPException(409,'Course already in this plan.')
        total=db.execute('SELECT coalesce(sum(credits),0) FROM learning_plans JOIN courses ON code=course_code WHERE user_id=? AND term=?',(user['id'],body.term)).fetchone()[0]
        if total+course['credits']>12:raise HTTPException(422,'This demonstration plan allows at most 12 credits per term.')
        db.execute('INSERT INTO learning_plans VALUES(?,?,?)',(user['id'],body.term,body.course_code))
    return {'ok':True}

@router.delete('/plan/{code}')
def remove(code:str,term:str=Query(default='2027 Semester 1',min_length=3,max_length=60),user=Depends(roles('student'))):
    with connect() as db:
        cur=db.execute('DELETE FROM learning_plans WHERE user_id=? AND term=? AND course_code=?',(user['id'],term,code))
        if not cur.rowcount:raise HTTPException(404,'Plan entry not found.')
    return {'ok':True}
