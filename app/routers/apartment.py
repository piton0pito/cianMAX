import base64
from typing import List

from fastapi import APIRouter, HTTPException, Response, Depends, UploadFile, File
from fastapi.responses import JSONResponse
from sqlmodel import Session, select
from datetime import datetime

from app.db import get_session
from app.models import Apartment, User, Message, PhotoApartment
from app.schemas import GetApartment, AddApartment, UpdateDescriptionApartment, CreateMessage, UpdateMessage, \
    PhotoResponse
from app.utils import verify_access_token, process_images, get_image_paths

router = APIRouter(tags=['apartment'],
                   responses={404: {"description": "Not found"}})


@router.post('/get_apartments/')
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

    offset = data.offset
    limit = data.limit
    query = query.offset(offset).limit(limit)

    apartments = session.exec(query).all()

    return apartments


@router.post('/get_apartment_data/{apartment_id}')
async def get_apartment(apartment_id: int, session: Session = Depends(get_session)):
    apartment = session.exec(select(Apartment).where(Apartment.id == apartment_id)).first()
    if not apartment:
        raise HTTPException(status_code=404)
    return apartment


@router.get('/get_apartment_photo_ids/{apartment_id}')
async def get_apartment(apartment_id: int, session: Session = Depends(get_session)):
    apartment = session.exec(select(Apartment).where(Apartment.id == apartment_id)).first()
    if not apartment:
        raise HTTPException(status_code=404)
    images = session.exec(select(PhotoApartment).where(PhotoApartment.apartment_id == apartment_id)).all()
    ids = []
    for photo in images:
        ids.append(photo.id)
    return {'apartment_ids': ids}


@router.get('/get_apartment_photo/{photo_id}')
async def get_apartment(photo_id: int, session: Session = Depends(get_session)):
    photo = session.exec(select(PhotoApartment).where(PhotoApartment.id == photo_id)).first()
    if not photo:
        raise HTTPException(status_code=404)
    return Response(content=photo.image, media_type="image/jpeg")


@router.post('/add_apartment/')
async def add_apartment(data: AddApartment,  # images: List[UploadFile] = File(...),
                        session: Session = Depends(get_session), user: User = Depends(verify_access_token)):
    # Обработка запроса
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
    session.add(apartment)
    session.commit()

    # Сохранение изображений в базу данных
    # for image in images:
    #     image_data = await image.read()
    #     image_instance = PhotoApartment(apartment_id=apartment.id, image=image_data)
    #     session.add(image_instance)
    #     session.commit()

    return JSONResponse(content={"message": "Квартира добавлена"}, status_code=201)


@router.post('/add_apartment/images/{apartment_id}', response_class=Response)
async def add_apartment_images(apartment_id: int, images: List[UploadFile] = File(...),
                               user: User = Depends(verify_access_token), session: Session = Depends(get_session)):
    apartment = session.exec(select(Apartment).where(Apartment.id == apartment_id)).first()
    if not apartment:
        raise HTTPException(status_code=404)
    if apartment.user_id != user.id:
        raise HTTPException(status_code=403)

    # Сохранение изображений в базу данных
    for image in images:
        image_data = await image.read()
        image_instance = PhotoApartment(apartment_id=apartment.id, image=image_data)
        session.add(image_instance)
        session.commit()
    return Response(status_code=200)


@router.put('/update_apartment/{data.apartment_id}/')
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


@router.put('/inactive_apartment/{apartment_id}')
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
