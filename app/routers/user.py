from fastapi import APIRouter, HTTPException, Response, Depends
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from pydantic import json
from sqlmodel import Session, select

from app.db import get_session
from app.models import User
from app.schemas import UserCreate, UserUpdate, Email, GetUser, CreateNewPassword
from app.utils import create_access_token, hash_password, verify_access_token, gen_res_key, send_mail

router = APIRouter(tags=['user'],
                   responses={404: {"description": "Not found"}})


@router.post('/login/')
async def login_user(response: Response,
                     session: Session = Depends(get_session),
                     data: OAuth2PasswordRequestForm = Depends()
                     ):
    user = session.exec(select(User).where(
        User.email == data.username)).first()  # так как у нас нет username как такогого, мы будем использовать email
    if not user or not user.verify_password(data.password):
        raise HTTPException(status_code=401,
                            detail='Incorrect email or password',
                            headers={"WWW-Authenticate": "Bearer"}
                            )
    access_token = create_access_token(data={"sub": user.id})
    response.set_cookie(key="access_token", value=access_token, httponly=True)
    return {"access_token": access_token, "token_type": "bearer"}


@router.post('/register/')
def reg_user(user: UserCreate,
             session: Session = Depends(get_session)
             ):
    temp_user = session.exec(select(User).where(User.email == user.email)).first()
    if temp_user:
        raise HTTPException(status_code=400,
                            detail='Email is busy')
    if user.password != user.complete_password:
        raise HTTPException(status_code=401, detail='Incorrect password')
    hashed_password = hash_password(user.password)
    db_user = User(email=user.email,
                   hash_password=hashed_password,
                   name=user.name,
                   )
    session.add(db_user)
    session.commit()
    raise HTTPException(status_code=201)


@router.post('/token')
def login_user_for_token(response: Response,
                         session: Session = Depends(get_session),
                         data: OAuth2PasswordRequestForm = Depends()
                         ):
    user = session.exec(select(User).where(
        User.email == data.username)).first()  # так как у нас нет username как такогого, мы будем использовать email
    if not user or not user.verify_password(data.password):
        raise HTTPException(status_code=401,
                            detail='Incorrect email or password',
                            headers={"WWW-Authenticate": "Bearer"}
                            )
    access_token = create_access_token(data={"sub": user.id})
    response.set_cookie(key="access_token", value=access_token, httponly=True)
    return {"access_token": access_token, "token_type": "bearer"}


@router.put('/update/')
def update_user_data(data: UserUpdate,
                     session: Session = Depends(get_session),
                     user: User = Depends(verify_access_token)
                     ):
    if session.exec(select(User).where(User.email == data.email)).first() and session.exec(select(User).where(User.email == data.email)).first().id != user.id:
        raise HTTPException(status_code=400, detail='Email is busy')
    if data.password != data.complete_password:
        raise HTTPException(status_code=401, detail='Incorrect password')
    user.email = data.email
    user.hash_password = hash_password(data.password)
    # print(user)
    session.add(user)
    session.commit()
    session.refresh(user)
    raise HTTPException(status_code=200)


@router.put('/reset_password/')
def reset_password(email: Email, session: Session = Depends(get_session)):
    temp_user = session.exec(select(User).where(User.email == email.email)).first()
    if not temp_user:
        raise HTTPException(status_code=401, detail='Incorrect email')
    code = gen_res_key()
    send_mail(temp_user.email, code)
    # print(code)
    temp_user.sqlmodel_update({'temp_data': code})
    session.add(temp_user)
    session.commit()
    session.refresh(temp_user)
    raise HTTPException(status_code=201)


@router.put('/create_new_password/')
def create_new_password(data: CreateNewPassword, session: Session = Depends(get_session)):
    temp_user = session.exec(select(User).where(User.email == data.email)).first()
    if not temp_user:
        raise HTTPException(status_code=400, detail='Incorrect email or code')
    if data.code != temp_user.temp_data:
        raise HTTPException(status_code=400, detail='Incorrect email or code')
    if data.password != data.complete_password:
        raise HTTPException(status_code=401, detail='Incorrect password')
    temp_user.sqlmodel_update({'hash_password': hash_password(data.password)})
    temp_user.sqlmodel_update(({'temp_data': None}))
    session.add(temp_user)
    session.commit()
    session.refresh(temp_user)
    raise HTTPException(status_code=200)


@router.get('/me/')
def user_me(temp_user: User = Depends(verify_access_token)):
    user = GetUser(email=temp_user.email, name=temp_user.name)
    return user
