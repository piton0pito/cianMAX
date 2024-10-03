from pydantic import BaseModel, Field, EmailStr
from datetime import datetime
from pydantic_extra_types.phone_numbers import PhoneNumber


class UserCreate(BaseModel):
    email: EmailStr = Field(default='Email')  # почта
    phone: PhoneNumber = Field(default='+78005553535')
    name: str = Field(default='Имя')  # имя
    password: str = Field(default='Password')
    complete_password: str = Field(default='Confirm the password')


class UserUpdate(BaseModel):
    email: EmailStr = Field(default='Email')
    password: str = Field(default='Password')
    complete_password: str = Field(default='Confirm the password')


class CreateNewPassword(BaseModel):
    email: EmailStr = Field(default='Email')
    code: str = Field(default='Verify code')
    password: str = Field(default='Password')
    complete_password: str = Field(default='Confirm the password')


class GetUser(BaseModel):
    email: EmailStr = Field(default='Email')  # почта
    name: str = Field(default='Имя')  # имя


class AddApartment(BaseModel):
    city: str = Field(default='None', description='city')
    address: str = Field(default='None', description='address')
    type: str = Field(default='None', description='type')
    m: int = Field(default='None', description='m')
    prise: int = Field(default='None', description='prise')
    description: str = Field(default='None', description='description')


class GetApartment(BaseModel):
    city: str = Field(default='None', description='city')
    type: str = Field(default='None', description='type')
    from_m: int = Field(default=-1, description='from_m')
    before_m: int = Field(default=-1, description='before_m')
    from_prise: int = Field(default=-1, description='from_prise')
    before_prise: int = Field(default=-1, description='before_prise')


class UpdateDescriptionApartment(BaseModel):
    apartments_id: int
    description: str


class Email(BaseModel):
    email: str


class CreateReview(BaseModel):
    apartment_id: int
    stars: int
    description: str = Field(default='description')
    anonim: bool = Field(default=False)


class UpdateReview(BaseModel):
    review_id: int
    description: str = Field(default='description')


class CreateMessage(BaseModel):
    apartment_id: int
    phone: bool = Field(defalt=True)
    description: str = Field(default='description')


class UpdateMessage(BaseModel):
    message_id: int
    description: str = Field(default='description')




