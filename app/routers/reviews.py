from fastapi import APIRouter, HTTPException, Response, Depends
from sqlmodel import Session, select
from datetime import datetime

from app.db import get_session
from app.models import Apartment, User, Review
from app.schemas import GetApartment, AddApartment, UpdateDescriptionApartment, CreateReview, UpdateReview
from app.utils import verify_access_token

router = APIRouter(tags=['reviews'],
                   responses={404: {"description": "Not found"}})


@router.get('/review/')
def review(session: Session = Depends(get_session)):
    review = session.exec(select(Review)).all()
    return review


@router.get('/review/{apartment_id}')
def review(apartment_id: int, session: Session = Depends(get_session)):
    review = session.exec(select(Review).where(Review.id == apartment_id)).all()
    return review


@router.post('/create_review/')
def create_review(data: CreateReview, user: User = Depends(verify_access_token),
                  session: Session = Depends(get_session)):
    if not (0 < data.stars <= 5):
        raise HTTPException(status_code=400)
    if session.exec(select(Review).where(Review.user_id == user.id).where(Review.apartment_id == data.apartment_id)).first():
        raise HTTPException(status_code=400, detail='You have review for this apartment')
    temp_review = Review(
        apartment_id=data.apartment_id,
        user_id=user.id,
        stars=data.stars,
        description=data.description
    )
    if data.anonim == False:
        temp_review.set_name(user.name)

    session.add(temp_review)
    session.commit()
    raise HTTPException(status_code=201)


@router.put('/update_review/{data.review_id}')
def update_review(data: UpdateReview, session: Session = Depends(get_session),
                  user: User = Depends(verify_access_token)):
    review = session.exec(select(Review).where(Review.id == data.review_id)).first()
    if not review:
        raise HTTPException(status_code=404)
    if review.user_id != user.id:
        raise HTTPException(status_code=403)
    review.edit_description(data.description)
    session.add(review)
    session.commit()
    session.refresh(review)
    raise HTTPException(status_code=200)


@router.delete('/delete_review/{review_id}')
def update_review(review_id, session: Session = Depends(get_session),
                  user: User = Depends(verify_access_token)):
    review = session.exec(select(Review).where(Review.id == review_id)).first()
    if not review:
        raise HTTPException(status_code=404)
    if review.user_id != user.id:
        raise HTTPException(status_code=403)
    session.delete(review)
    session.commit()
    raise HTTPException(status_code=200)


