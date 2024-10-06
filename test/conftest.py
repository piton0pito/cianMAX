import pytest
from fastapi.security import HTTPBasic
from sqlalchemy import delete
from sqlmodel import create_engine, Session, SQLModel, select
from starlette.testclient import TestClient

from app.config import TEST_USER_PASSWORD, TEST_USER_EMAIL, TEST_USER_NAME, TEST_USER_PHONE, PASS_ADMIN, EMAIL_ADMIN
from app.db import get_session
from app.main import app
from app.models import User, Apartment, Review, Message, Avatar, PhotoApartment
from app.utils import hash_password
from test.data_for_test import email_data

engine = create_engine("sqlite:///./test_data_base.db")
security = HTTPBasic()
client = TestClient(app)


def override_get_session():
    with Session(engine) as session:
        yield session


@pytest.fixture(autouse=True, scope='session')
def over_depends():
    app.dependency_overrides[get_session] = override_get_session
    yield


@pytest.fixture(scope='function')
def session():
    yield Session(engine)


@pytest.fixture(autouse=True, scope='session')
def setup():
    SQLModel.metadata.create_all(engine)
    yield
    SQLModel.metadata.drop_all(engine)


@pytest.fixture(scope='function', autouse=False)
def clear_database(session):
    yield
    session = Session(engine)
    session.exec(delete(User))
    session.exec(delete(Apartment))
    session.exec(delete(Review))
    session.exec(delete(Message))
    session.exec(delete(Avatar))
    session.exec(delete(PhotoApartment))
    session.commit()
    session.close()


@pytest.fixture(scope="function")
def add_test_user_1(session):
    hash_pass = hash_password(TEST_USER_PASSWORD)
    user_1 = User(email=TEST_USER_EMAIL,
                  hash_password=hash_pass,
                  name=TEST_USER_NAME,
                  phone=TEST_USER_PHONE
                  )
    session.add(user_1)
    session.commit()
    session.close()
    response = client.post("/login/", data={
        "grant_type": "password",
        "username": TEST_USER_EMAIL,
        "password": TEST_USER_PASSWORD
    })
    assert response.status_code == 200
    return response.json()["access_token"]


@pytest.fixture(scope="function")
def add_test_user_2(session):
    hash_pass = hash_password(TEST_USER_PASSWORD)
    user_2 = User(email=TEST_USER_EMAIL + 'test',
                  hash_password=hash_pass,
                  name=TEST_USER_NAME,
                  phone=TEST_USER_PHONE
                  )
    session.add(user_2)
    session.commit()
    session.close()
    response = client.post("/login/", data={
        "grant_type": "password",
        "username": TEST_USER_EMAIL + 'test',
        "password": TEST_USER_PASSWORD
    })
    assert response.status_code == 200
    return response.json()["access_token"]


@pytest.fixture(scope="function")
def add_test_admin_1(session):
    hash_pass = hash_password(PASS_ADMIN)
    admin_1 = User(email=EMAIL_ADMIN,
                   hash_password=hash_pass,
                   name='admin',
                   phone=TEST_USER_PHONE
                   )
    admin_1.super_user()
    session.add(admin_1)
    session.commit()
    session.close()
    response = client.post("/login/", data={
        "grant_type": "password",
        "username": EMAIL_ADMIN,
        "password": PASS_ADMIN
    })
    assert response.status_code == 200
    return response.json()["access_token"]


@pytest.fixture(scope="function")
def add_test_admin_2(session):
    hash_pass = hash_password(PASS_ADMIN)
    admin_2 = User(email=EMAIL_ADMIN + 'test',
                   hash_password=hash_pass,
                   name='admin',
                   phone=TEST_USER_PHONE
                   )
    admin_2.super_user()
    session.add(admin_2)
    session.commit()
    session.close()
    response = client.post("/login/", data={
        "grant_type": "password",
        "username": EMAIL_ADMIN + 'test',
        "password": PASS_ADMIN
    })
    assert response.status_code == 200
    return response.json()["access_token"]


@pytest.fixture(scope='function')
def get_code(session):
    response = client.put("/reset_password/", json=email_data)
    assert response.status_code == 201
    code = session.exec(select(User)).first().temp_data
    session.close()
    return code
