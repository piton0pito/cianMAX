from fastapi import APIRouter, HTTPException, Response, Depends
from sqlmodel import Session, select
from datetime import datetime

from app.db import get_session
from app.models import Apartment, User
from app.schemas import GetApartment, AddApartment
from app.utils import verify_access_token

router = APIRouter(tags=['apartment'],
                   responses={404: {"description": "Not found"}})


@router.post('/get_apartment/')  # это post запрос, так как для get запроса слишком большой обьем отправляемой инормации
def get_apartment_temp(data: GetApartment, session: Session = Depends(get_session)):
    print(data)
    return session.exec(select(Apartment).where(Apartment.city == data.city).where(Apartment.type == data.type).where(
        Apartment.m >= data.from_m).where(Apartment.m <= data.before_m).where(Apartment.prise >= data.from_prise).where(
        Apartment.prise <= data.before_prise))


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
    print(apartment)
    session.add(apartment)
    session.commit()
    raise HTTPException(status_code=200)
