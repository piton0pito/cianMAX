from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import FileResponse
from sqlmodel import Session, select

from app.config import PASS_ADMIN, EMAIL_ADMIN
from app.db import get_session
from app.models import User, Apartment
from app.schemas import AddApartment
from app.utils import hash_password, verify_access_token, get_xlsx

router = APIRouter(prefix='/admin', tags=['admin'],
                   responses={404: {"description": "Not found"}})


@router.post('/create_first_admin/')
def create_admin(session: Session = Depends(get_session)):
    if session.exec(select(User).where(User.role == 'super_user')).first():
        raise HTTPException(status_code=400)
    hash_pass = hash_password(PASS_ADMIN)
    user = User(email=EMAIL_ADMIN,
                hash_password=hash_pass,
                first_name='admin',
                last_name='admin',
                surname='admin',
                license='0000000000',
                )
    user.super_user()
    session.add(user)
    session.commit()
    raise HTTPException(status_code=201)


@router.get('/get_all_user/')
def get_all_user(user: User = Depends(verify_access_token), session: Session = Depends(get_session)):
    if user.role != 'super_user':
        raise HTTPException(status_code=403)
    users = session.exec(select(User)).all()
    return users


@router.get('/get_user/xlsx')
def get_verify_user(user: User = Depends(verify_access_token), session: Session = Depends(get_session)):
    if user.role != 'super_user':
        raise HTTPException(status_code=403)
    name = 'users'
    users = session.exec(select(User).where(User.role == 'verify')).all()
    get_xlsx(users, f'{name}.xlsx')
    return FileResponse(path=f'media_data/{name}.xlsx', filename=f'{name}.xlsx', media_type='multipart/form-data')


@router.put('/BAN_user/{user_id}')
def get_no_verify_user(user_id: int, su_user: User = Depends(verify_access_token),
                       session: Session = Depends(get_session)):
    if su_user.role != 'super_user':
        raise HTTPException(status_code=403)
    user = session.exec(select(User).where(User.id == user_id)).first()
    if not user:
        raise HTTPException(status_code=404, detail='User not found')
    if user.role == 'BAN':
        raise HTTPException(status_code=400, detail='The user has already been blocked')
    user.ban_user()
    session.add(user)
    session.commit()
    session.refresh(user)
    raise HTTPException(status_code=200)


@router.put('/un_BAN_user/{user_id}')
def get_no_verify_user(user_id: int, su_user: User = Depends(verify_access_token),
                       session: Session = Depends(get_session)):
    if su_user.role != 'super_user':
        raise HTTPException(status_code=403)
    user = session.exec(select(User).where(User.id == user_id)).first()
    if not user:
        raise HTTPException(status_code=404, detail='User not found')
    if user.role != 'BAN':
        raise HTTPException(status_code=400, detail='The user is not blocked')
    user.user_user()
    session.add(user)
    session.commit()
    session.refresh(user)
    raise HTTPException(status_code=200)


@router.delete('/del_user/{user_id}')
def del_user(user_id: int, su_user: User = Depends(verify_access_token), session: Session = Depends(get_session)):
    if su_user.role != 'super_user':
        raise HTTPException(status_code=403)
    user = session.exec(select(User).where(User.id == user_id)).first()
    if not user:
        raise HTTPException(status_code=404, detail='User not found')
    session.delete(user)
    session.commit()
    raise HTTPException(status_code=204)


@router.put('/make_super_user/{user_id}')
def get_no_verify_user(user_id: int, su_user: User = Depends(verify_access_token),
                       session: Session = Depends(get_session)):
    if su_user.role != 'super_user':
        raise HTTPException(status_code=403)
    user = session.exec(select(User).where(User.id == user_id)).first()
    if not user:
        raise HTTPException(status_code=404, detail='User not found')
    if user.role == 'BAN':
        raise HTTPException(status_code=400, detail='The user has already been blocked')
    if user.role == 'super_user':
        raise HTTPException(status_code=400, detail='The user is already a super user')
    user.super_user()
    session.add(user)
    session.commit()
    session.refresh(user)
    raise HTTPException(status_code=200)


@router.put('/un_make_super_user/{user_id}')
def get_no_verify_user(user_id: int, su_user: User = Depends(verify_access_token),
                       session: Session = Depends(get_session)):
    if su_user.role != 'super_user':
        raise HTTPException(status_code=403)
    user = session.exec(select(User).where(User.id == user_id)).first()
    if not user:
        raise HTTPException(status_code=404, detail='User not found')
    if user.role != 'super_user':
        raise HTTPException(status_code=400, detail='The user is not a super user')
    user.user_user()
    session.add(user)
    session.commit()
    session.refresh(user)
    raise HTTPException(status_code=200)


# @router.get('/get_all_apartment/')
# def get_all_cars(session: Session = Depends(get_session), su_user: User = Depends(verify_access_token)):
#     if su_user.role != 'super_user':
#         raise HTTPException(status_code=403)
#     return session.exec(select(Apartment)).all()


@router.delete('/del_apartment/{apartment_id}')
def del_apartment(apartment_id: int, su_user: User = Depends(verify_access_token),
                  session: Session = Depends(get_session)):
    if su_user.role != 'super_user':
        raise HTTPException(status_code=403)
    apartment = session.exec(select(Apartment).where(Apartment.id == apartment_id)).first()
    if not apartment:
        raise HTTPException(status_code=404)
    session.delete(apartment)
    session.commit()
    raise HTTPException(status_code=200)


@router.delete('/del_review/{review_id}')
def del_review(review_id: int, su_user: User = Depends(verify_access_token),
               session: Session = Depends(get_session)):
    if su_user.role != 'super_user':
        raise HTTPException(status_code=403)
    apartment = session.exec(select(Apartment).where(Apartment.id == review_id)).first()
    if not apartment:
        raise HTTPException(status_code=404)
    session.delete(apartment)
    session.commit()
    raise HTTPException(status_code=200)


@router.delete('/del_review/{message_id}')
def del_review(message_id: int, su_user: User = Depends(verify_access_token),
               session: Session = Depends(get_session)):
    if su_user.role != 'super_user':
        raise HTTPException(status_code=403)
    apartment = session.exec(select(Apartment).where(Apartment.id == message_id)).first()
    if not apartment:
        raise HTTPException(status_code=404)
    session.delete(apartment)
    session.commit()
    raise HTTPException(status_code=200)
