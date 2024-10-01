from pydantic import BaseModel, Field, EmailStr
from datetime import datetime


class UserCreate(BaseModel):
    email: EmailStr = Field(default='Email')  # почта
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
    city: str = Field(default='city')
    address: str = Field(default='address')
    type: str = Field(default='type')
    m: int = Field(default='m')
    prise: int = Field(default='prise')
    description: str = Field(default='description')


class GetApartment(BaseModel):
    city: str = Field(default=None, description='city')
    type: str = Field(default=None, description='type')
    from_m: int = Field(default=None, description='from_m')
    before_m: int = Field(default=None, description='before_m')
    from_prise: int = Field(default=None, description='from_prise')
    before_prise: int = Field(default=None, description='before_prise')



class UpdateDescriptionApartment(BaseModel):
    apartments_id: int
    description: str


class Email(BaseModel):
    email: str
