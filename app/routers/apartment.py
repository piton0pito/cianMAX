from fastapi import APIRouter, HTTPException, Response, Depends
from sqlmodel import Session, select
from datetime import datetime

from app.db import get_session
from app.models import Apartment, User, Message
from app.schemas import GetApartment, AddApartment, UpdateDescriptionApartment, CreateMessage, UpdateMessage
from app.utils import verify_access_token

router = APIRouter(tags=['apartment'],
                   responses={404: {"description": "Not found"}})


@router.post('/get_apartment/')  # это post запрос, так как для get запроса слишком большой обьем отправляемой инормации
def get_apartment_temp(data: GetApartment, session: Session = Depends(get_session)):
    query = select(Apartment)

    if data.city != 'None':
        query = query.where(Apartment.city == data.city)
    if data.type != 'None':
        query = query.where(Apartment.type == data.type)
    if data.from_m != -1:
        query = query.where(Apartment.month >= data.from_m)
    if data.before_m != -1:
        query = query.where(Apartment.month <= data.before_m)
    if data.from_prise != -1:
        query = query.where(Apartment.price >= data.from_prise)
    if data.before_prise != -1:
        query = query.where(Apartment.price <= data.before_prise)

    apartment = session.exec(query).all()
    return apartment


@router.post('/add_apartment/')
def add_apartment(data: AddApartment, session: Session = Depends(get_session),
                  user: User = Depends(verify_access_token)):
    apartment = Apartment(
        user_id=user.id,
        user_name=user.name,
        address=data.address,
        city=data.city,
        type=data.type,
        m=data.m,
        prise=data.prise,
        description=data.description
    )
    # print(apartment)
    session.add(apartment)
    session.commit()
    raise HTTPException(status_code=201)


@router.put('/update/{data.apartment_id}/')
def update_description_apartment(data: UpdateDescriptionApartment, session: Session = Depends(get_session),
                                 user: User = Depends(verify_access_token)):
    apartment = session.exec(select(Apartment).where(Apartment.id == data.apartments_id)).first()
    if apartment.user_id == user.id:
        raise HTTPException(status_code=403)
    if not apartment:
        raise HTTPException(status_code=404)
    apartment.edit_description(data.description)
    session.add(apartment)
    session.commit()
    session.refresh(apartment)
    raise HTTPException(status_code=200)


@router.put('/inactive/{apartment_id}')
def inactive_apartment(apartment_id: int, user: User = Depends(verify_access_token),
                       session: Session = Depends(get_session)):
    apartment = session.exec(select(Apartment).where(Apartment.id == apartment_id)).first()
    if apartment.user_id == user.id:
        raise HTTPException(status_code=403)
    if not apartment:
        raise HTTPException(status_code=404)
    apartment.inactive()
    session.add(apartment)
    session.commit()
    session.refresh(apartment)
    raise HTTPException(status_code=200)


@router.get('/user_apartment/{user_id}')
def user_apartment(user_id: int, session: Session = Depends(get_session)):
    apartments = session.exec(select(Apartment).where(Apartment.user_id == user_id)).all()
    if not apartments:
        raise HTTPException(status_code=404, detail='No apartment')
    return apartments

