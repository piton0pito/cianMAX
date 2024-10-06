import os
from pathlib import Path
from typing import Annotated
from PIL import Image

from fastapi import APIRouter, HTTPException, Response, Depends, UploadFile, File
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from pydantic import json
from sqlmodel import Session, select
from starlette.responses import FileResponse

from app.db import get_session
from app.models import User, Apartment, Avatar
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
                   phone=user.phone,
                   hash_password=hashed_password,
                   name=user.name,
                   )
    # print(db_user)
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
    if session.exec(select(User).where(User.email == data.email)).first() and session.exec(
            select(User).where(User.email == data.email)).first().id != user.id:
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
    data.code = hash_password(data.code)
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
def user_me(temp_user: User = Depends(verify_access_token), session: Session = Depends(get_session)):
    user = GetUser(email=temp_user.email, name=temp_user.name)
    apartments = session.exec(select(Apartment).where(Apartment.user_id == temp_user.id)).all()
    # avatar = session.exec(select(Avatar).where(Avatar.user_id == temp_user.id)).first()
    return user, apartments


@router.get('/my_avatar/')
def user_me(temp_user: User = Depends(verify_access_token), session: Session = Depends(get_session)):
    avatar = session.exec(select(Avatar).where(Avatar.user_id == temp_user.id)).first()
    if not avatar:
        avatar = session.exec(select(Avatar).where(Avatar.user_id == 1)).first()
    return Response(content=avatar.image, media_type="image/jpeg")


@router.get('/user/{user_id}')
def user_me(user_id: int, session: Session = Depends(get_session)):
    user = session.exec(select(User).where(User.id == user_id)).first()
    apartments = session.exec(select(Apartment).where(Apartment.user_id == user_id)).all()
    # avatar = session.exec(select(Avatar).where(Avatar.user_id == temp_user.id)).first()
    return user, apartments


@router.get("/get_avatar/{user_id}")
async def get_ava(user_id: int, session: Session = Depends(get_session)):
    user = session.exec(select(User).where(User.id == user_id)).first()
    if not user:
        raise HTTPException(status_code=404)
    avatar = session.exec(select(Avatar).where(Avatar.user_id == user_id)).first()
    if not avatar:
        avatar = session.exec(select(Avatar).where(Avatar.user_id == 1)).first()
    return Response(content=avatar.image, media_type="image/jpeg")


@router.post("/upload_avatar/")
async def create_avatar(file: UploadFile = File(...), user: User = Depends(verify_access_token),
                        session: Session = Depends(get_session)):
    image_db = session.exec(select(Avatar).where(Avatar.user_id == user.id)).first()
    image_data = await file.read()

    # Check file size
    if len(image_data) > 2 * 1024 * 1024:
        raise HTTPException(status_code=413, detail="File too large. Maximum size is 2MB.")
    if not image_db:
        image_instance = Avatar(user_id=user.id, image=image_data)
        session.add(image_instance)
        session.commit()
        raise HTTPException(status_code=200)
    else:
        image_db.update_avatar(image_data)
        session.add(image_db)
        session.commit()
        session.refresh(image_db)
        raise HTTPException(status_code=200)
