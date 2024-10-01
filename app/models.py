from sqlmodel import SQLModel, Field
from typing import Optional
from datetime import datetime
from hashlib import sha256


class User(SQLModel, table=True):
    id: Optional[int] = Field(primary_key=True, default=None)
    hash_password: str  # хэш пароля
    role: str = Field(default='no_verify')  # роль пользователя super_user, moderate, user, BAN
    email: str = Field()  # почта
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
    description: str

    def edit_description(self, description):
        self.description = description

    def inactive(self):
        self.status = 'inactive'

    def active(self):
        self.status = 'active'


class Reviews(SQLModel, tadle=True):
    id: Optional[int] = Field(primary_key=True, default=None)
    user_id: int = Field(foreign_key='user.id')
    stars: int = Field(ge=0, le=5)
    description: str

    def edit_description(self, description):
        self.description = description


class Messages(SQLModel, table=True):
    id: Optional[int] = Field(primary_key=True, default=None)
    create_user_id: int = Field(foreign_key='user.id')
    recipient_user_id: int
    description: str
