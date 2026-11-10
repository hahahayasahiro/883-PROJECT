import hmac
import secrets
import time
from fastapi import APIRouter, Depends, HTTPException, Request, Response
from pydantic import BaseModel, Field
from .db import connect, password_hash

router = APIRouter(prefix='/api/auth', tags=['Authentication'])


def current_user(request: Request):
    with connect() as db:
        row = db.execute('SELECT users.* FROM sessions JOIN users ON users.id=sessions.user_id WHERE token=? AND expires>?', (request.cookies.get('campus_session',''), time.time())).fetchone()
    if not row:
        raise HTTPException(401, 'Please sign in.')
    return {k: row[k] for k in ['id','username','name','role','student_id','email']}


def roles(*allowed):
    def guard(user=Depends(current_user)):
        if user['role'] not in allowed:
            raise HTTPException(403, 'Your role cannot perform this action.')
        return user
    return guard


class Login(BaseModel):
    username: str = Field(max_length=80)
    password: str = Field(max_length=200)


@router.post('/login')
def login(body: Login, response: Response):
    with connect() as db:
        user = db.execute('SELECT * FROM users WHERE username=?', (body.username,)).fetchone()
        if not user or not hmac.compare_digest(password_hash(body.password,user['salt']),user['password_hash']):
            raise HTTPException(401,'Incorrect username or password.')
        token = secrets.token_urlsafe(32)
        db.execute('DELETE FROM sessions WHERE expires<?', (time.time(),))
        db.execute('INSERT INTO sessions VALUES(?,?,?)', (token,user['id'],time.time()+28800))
    response.set_cookie('campus_session',token,httponly=True,samesite='strict',max_age=28800)
    return {'name':user['name'], 'role':user['role']}


@router.get('/me')
def me(user=Depends(current_user)):
    return user


@router.post('/logout')
def logout(request: Request, response: Response):
    with connect() as db:
        db.execute('DELETE FROM sessions WHERE token=?',(request.cookies.get('campus_session',''),))
    response.delete_cookie('campus_session')
    return {'ok':True}
