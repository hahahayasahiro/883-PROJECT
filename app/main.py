from contextlib import asynccontextmanager
from dotenv import load_dotenv
from fastapi import FastAPI, Request, HTTPException
from fastapi.staticfiles import StaticFiles
from .db import ROOT, initialize
from .auth import router as auth_router
from .routers import assistant,learning,facilities,maintenance,reviews,applications

load_dotenv(ROOT / '.env')


@asynccontextmanager
async def lifespan(app):
    initialize()
    yield


app=FastAPI(title='SmartCampus Prototype',version='0.1.0',lifespan=lifespan)


@app.middleware('http')
async def local_origin(request:Request, call_next):
    origin=request.headers.get('origin')
    if request.method not in ('GET','HEAD','OPTIONS') and origin and origin!=str(request.base_url).rstrip('/'):
        from fastapi.responses import JSONResponse
        return JSONResponse({'detail':'Cross-origin requests are not allowed.'},status_code=403)
    response=await call_next(request)
    response.headers['X-Content-Type-Options']='nosniff'
    response.headers['Referrer-Policy']='same-origin'
    response.headers['Cache-Control']='no-store'
    response.headers['Content-Security-Policy']="default-src 'self'; script-src 'self'; style-src 'self'; img-src 'self' data:; connect-src 'self'; frame-ancestors 'none'"
    return response


@app.get('/api/health')
def health():
    return {'status':'ok','prototype':True}


for router in [auth_router,assistant.router,learning.router,facilities.router,maintenance.router,reviews.router,applications.router]:
    app.include_router(router)
app.mount('/',StaticFiles(directory=ROOT/'static',html=True),name='web')
