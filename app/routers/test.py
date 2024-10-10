from typing import List, Optional

from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from sqlmodel import Session

from app.db import get_session
from app.models import User, Apartment
from app.schemas import AddApartment
from app.utils import process_images, verify_access_token

router = APIRouter(tags=['test'],
                   responses={404: {"description": "Not found"}})


@router.post("/send_images")
async def update_item(
        files: List[UploadFile] or None,
):
    if not files:
        print('none')
    print(type(files), files[0])
    return {"res": len(files)}


@router.post("/upload_images/")
async def upload_images(images: Optional[List[UploadFile]] = File(...)):
    print(type(images))
    if not images:
        return 'ok'
    result = await process_images(images, target_dir="media", target_name="image")
    return result


@router.post('/add_apartmentdd/')
def add_apartment(images: List[UploadFile]):
    print(images)
    # apartment = Apartment(
    #     user_id=user.id,
    #     user_name=user.name,
    #     address=data.address,
    #     city=data.city,
    #     type=data.type,
    #     m=data.m,
    #     prise=data.prise,
    #     description=data.description
    # )
    process_images(images, 'media', 'gg')
    raise HTTPException(status_code=201)
