from sqlmodel import SQLModel, Field
from typing import Optional
from datetime import datetime
from hashlib import sha256


class User(SQLModel, table=True):
    id: Optional[int] = Field(primary_key=True, default=None)
    hash_password: str  # хэш пароля
    role: str = Field(default='user')  # роль пользователя super_user, moderate, user, BAN
    email: str   # почта
    phone: str
    name: str  # имя
    date_reg: datetime = Field(default_factory=datetime.utcnow)  # дата регистрации
    temp_data: str = Field(nullable=True)

    def verify_password(self, password):
        return self.hash_password == sha256(password.encode()).hexdigest()

    def moderate_user(self):
        self.role = 'moderate'

    def ban_user(self):
        self.role = 'BAN'

    def super_user(self):
        self.role = 'super_user'

    def user_user(self):
        self.role = 'user'


class Apartment(SQLModel, table=True):
    id: Optional[int] = Field(primary_key=True, default=None)
    user_id: int = Field(foreign_key='user.id')
    user_name: str = Field(foreign_key='user.name')
    status: str = Field(default='active')  # inactive, active
    address: str
    city: str
    type: str
    m: int
    prise: int
    data: datetime = Field(default_factory=datetime.utcnow)
    description: str

    def edit_description(self, description):
        self.description = description

    def inactive(self):
        self.status = 'inactive'

    def active(self):
        self.status = 'active'


class Review(SQLModel, table=True):
    id: Optional[int] = Field(primary_key=True, default=None)
    apartment_id: int = Field(foreign_key='apartment.id')
    user_id: int = Field(foreign_key='user.id')
    user_name: str = Field(default='Anonim')
    stars: int = Field(gt=0, le=5)
    description: str
    data: datetime = Field(default_factory=datetime.utcnow)
    red: bool = Field(default=False)

    def edit_description(self, description):
        self.description = description
        self.red = True

    def set_name(self, name):
        self.user_name = name


class Message(SQLModel, table=True):
    id: Optional[int] = Field(primary_key=True, default=None)
    create_user_id: int = Field(foreign_key='user.id')
    recipient_user_id: int
    create_user_email: str = Field(foreign_key='user.email')
    create_user_phone: str = Field(nullable=True)
    description: str
    red: bool = Field(default=False)

    def set_phone(self, phone):
        self.create_user_phone = phone

    def edit_description(self, description):
        self.description = description
        self.red = True
