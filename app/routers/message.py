from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select

from app.db import get_session
from app.models import Apartment, Message, User
from app.schemas import CreateMessage, UpdateMessage
from app.utils import verify_access_token

router = APIRouter(tags=['message'],
                   responses={404: {"description": "Not found"}})


@router.post('/create_message/')
def create_message(data: CreateMessage, user: User = Depends(verify_access_token),
                   session: Session = Depends(get_session)):
    apartment = session.exec(select(Apartment).where(Apartment.id == data.apartment_id)).first()
    if not apartment:
        raise HTTPException(status_code=404)

    message = Message(
        create_user_id=user.id,
        recipient_user_id=apartment.user_id,
        create_user_email=user.email,
        description=data.description
    )
    if data.phone:
        message.set_phone(user.phone)

    session.add(message)
    session.commit()
    raise HTTPException(status_code=200)


@router.put('/update_message/')
def update_description(data: UpdateMessage, user: User = Depends(verify_access_token),
                       session: Session = Depends(get_session)):
    message = session.exec(select(Message).where(Message.id == data.message_id)).first()
    if not message:
        raise HTTPException(status_code=404)
    if message.create_user_id != user.id:
        raise HTTPException(status_code=403)
    message.edit_description(data.description)
    session.add(message)
    session.commit()
    session.refresh(message)
    raise HTTPException(status_code=200)


@router.delete('/delite_message/{message_id}')
def delite_message(message_id: int, user: User = Depends(verify_access_token), session: Session = Depends(get_session)):
    message = session.exec(select(Message).where(Message.id == message_id)).first()
    if not message:
        raise HTTPException(status_code=404)
    if message.create_user_id != user.id:
        raise HTTPException(status_code=403)
    session.delete(message)
    session.commit()
    raise HTTPException(status_code=200)


@router.get('/my_incoming_message/')
def my_incoming_message(user: User = Depends(verify_access_token), session: Session = Depends(get_session)):
    messages = session.exec(select(Message).where(Message.recipient_user_id == user.id)).all()
    return {'messages': messages}


@router.get('/my_outgoing_message/')
def my_outgoing_message(user: User = Depends(verify_access_token), session: Session = Depends(get_session)):
    messages = session.exec(select(Message).where(Message.create_user_id == user.id)).all()
    return {'messages': messages}
