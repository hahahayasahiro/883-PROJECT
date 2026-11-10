import json
import re
from typing import Literal
from fastapi import APIRouter,Depends,HTTPException,UploadFile,File
from pydantic import BaseModel,Field,ConfigDict
from ..auth import roles
from ..db import connect,rows
from .. import ai
from ..documents import extract,MAX_SIZE
from .applications import owned,check

router=APIRouter(prefix='/api/reviews',tags=['M3.1 Pre-review'])
class Review(BaseModel):
    application_id:int
class TextInput(BaseModel):
    text:str=Field(min_length=1,max_length=60000)
class Candidate(BaseModel):
    model_config=ConfigDict(extra='forbid')
    field:Literal['student_id','full_name','email','purpose','certificate_type']
    value:str=Field(min_length=1,max_length=2000)
    evidence:str=Field(min_length=1,max_length=2000)
class Extraction(BaseModel):
    model_config=ConfigDict(extra='forbid')
    candidates:list[Candidate]=Field(max_length=5)
class Finding(BaseModel):
    model_config=ConfigDict(extra='forbid')
    label:str=Field(min_length=1,max_length=160)
    status:Literal['pass','warning','fail']
    evidence:str=Field(min_length=1,max_length=2000)
    suggestion:str=Field(min_length=1,max_length=1000)
class Analysis(BaseModel):
    model_config=ConfigDict(extra='forbid')
    summary:str=Field(min_length=1,max_length=2000)
    checks:list[Finding]=Field(max_length=12)

@router.get('/checklist/{kind}')
def checklist(kind:Literal['transcript','certificate'],user=Depends(roles('student','admin'))):
    fields=['student_id','full_name','email','purpose']+(['certificate_type'] if kind=='certificate' else [])
    return {'kind':kind,'required_fields':fields,'materials':['A supporting statement with your student ID and purpose']+(['Certificate type and intended use'] if kind=='certificate' else []),'notice':'Synthetic demonstration checklist. AI pre-review is advisory.'}

@router.post('/upload')
async def upload(file:UploadFile=File(...),user=Depends(roles('student'))):
    try:
        data=await file.read(MAX_SIZE+1)
        return extract(data,file.filename or '')
    finally:await file.close()

@router.post('/extract')
async def suggestions(body:TextInput,user=Depends(roles('student'))):
    result=await ai.structured('Extract explicit application fields only. Return candidates as objects with field,value,evidence. Allowed fields: student_id,full_name,email,purpose,certificate_type. Each evidence must be an exact quotation from the material; each value must appear in that evidence. Do not invent absent fields.',{'material':body.text},Extraction)
    valid=[c.model_dump() for c in result.candidates if c.evidence in body.text and c.value.casefold() in c.evidence.casefold()] if result else []
    return {'mode':'live_ai' if result else 'manual','candidates':valid,'notice':'Review each candidate, then explicitly apply selected values. Existing fields are not overwritten automatically.'}

@router.post('')
async def review(body:Review,user=Depends(roles('student'))):
    with connect() as db:item=dict(owned(db,body.application_id,user))
    if item['status']!='draft':raise HTTPException(409,'Save a draft revision before pre-review.')
    fields=json.loads(item['fields'])
    issues=check(fields,item['kind'],user)
    checks=[{'label':'Required fields and identity','status':'fail' if issues else 'pass','evidence':'; '.join(issues) if issues else 'Required fields match the signed-in student.','suggestion':'Correct the listed fields.' if issues else 'Keep these identity fields unchanged.','source':'rules'}]
    ids=re.findall(r'\bS\d{4,}\b',item['material'],flags=re.I)
    if any(s.upper()!=user['student_id'] for s in ids):
        issue='Material contains a different student ID: '+', '.join(ids)
        issues.append(issue);checks.append({'label':'Student ID in material','status':'fail','evidence':', '.join(ids),'suggestion':'Use the signed-in student ID '+user['student_id'],'source':'rules'})
    result=await ai.structured('Pre-review fictional campus material against application fields. Return summary and checks, each with label,status(pass,warning,fail),evidence,suggestion. Evidence must be an exact excerpt of material or a field value. Identify possible inconsistencies. Do not approve applications or invent rules.',{'fields':fields,'material':item['material']},Analysis)
    evidence_text=item['material']+'\n'+'\n'.join(fields.values())
    valid=[{**c.model_dump(),'source':'ai'} for c in result.checks if c.evidence in evidence_text] if result else []
    # If structured output lacks verifiable evidence, retain rules and label AI unavailable.
    ai_valid=bool(result and valid)
    checks.extend(valid)
    issues.extend(c['label']+': '+c['evidence'] for c in valid if c['status']!='pass')
    output={'issues':issues,'checks':checks,'analysis':result.summary if ai_valid else 'AI unavailable or no verifiable AI evidence returned. Deterministic field and ID checks remain available.','mode':'live_ai' if ai_valid else 'rules_only','version':item['version'],'notice':'Pre-review is advisory. Administrative staff make the final decision.'}
    with connect() as db:
        db.execute('BEGIN IMMEDIATE')
        current=owned(db,body.application_id,user)
        if current['version']!=item['version'] or current['status']!='draft':raise HTTPException(409,'Application changed during review. Please review again.')
        db.execute('INSERT INTO reviews(application_id,result,version) VALUES(?,?,?)',(body.application_id,json.dumps(output),item['version']))
    return output

@router.get('/{aid}')
def history(aid:int,user=Depends(roles('student','admin'))):
    with connect() as db:current=owned(db,aid,user,staff=True)
    return [{**json.loads(r['result']),'id':r['id'],'created':r['created'],'version':r['version'],'stale':r['version']!=current['version']} for r in rows('SELECT * FROM reviews WHERE application_id=? ORDER BY id DESC',(aid,))]

@router.get('/{aid}/versions')
def versions(aid:int,user=Depends(roles('student','admin'))):
    with connect() as db:owned(db,aid,user,staff=True)
    result=rows('SELECT * FROM application_versions WHERE application_id=? ORDER BY version',(aid,))
    previous=None
    for v in result:
        v['fields']=json.loads(v['fields'])
        v['changes']=[]
        if previous:
            for key in sorted(set(previous['fields'])|set(v['fields'])):
                if previous['fields'].get(key,'')!=v['fields'].get(key,''):v['changes'].append({'field':key,'before':previous['fields'].get(key,''),'after':v['fields'].get(key,'')})
            for key in ['kind','material','file_name']:
                if previous[key]!=v[key]:v['changes'].append({'field':key,'before':previous[key],'after':v[key]})
        previous=v
    return result
