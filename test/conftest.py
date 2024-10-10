import pytest
from fastapi.security import HTTPBasic
from sqlalchemy import delete
from sqlmodel import create_engine, Session, SQLModel, select
from starlette.testclient import TestClient

from app.config import TEST_USER_PASSWORD, TEST_USER_EMAIL, TEST_USER_NAME, TEST_USER_PHONE, PASS_ADMIN, EMAIL_ADMIN, \
    TEST_APARTMENT_ADDRESS, TEST_APARTMENT_CITY, TEST_APARTMENT_TYPE, TEST_APARTMENT_M, TEST_APARTMENT_PRISE, \
    TEST_APARTMENT_DESCRIPTION, TEST_REVIEW_STARS, TEST_REVIEW_DESCRIPTION
from app.db import get_session
from app.main import app
from app.models import User, Apartment, Review, Message, Avatar, PhotoApartment
from app.utils import hash_password
from test.data_for_test import email_data, add_apartment_data, review_data

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


@pytest.fixture(scope='function')
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
    # print(response.json()["access_token"])
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


@pytest.fixture(scope='function')
def add_user_apartment_1(add_test_user_1, session):
    login = add_test_user_1
    # print(add_apartment_data)
    apartment_response = client.post('/add_apartment/', json=add_apartment_data, headers={"Authorization": f"Bearer {login}"})
    assert apartment_response.status_code == 201
    return add_test_user_1


@pytest.fixture(scope='function')
def add_user_apartment_2(add_test_user_2, session):
    response = client.post("/login/", data={
        "grant_type": "password",
        "username": TEST_USER_EMAIL + 'test',
        "password": TEST_USER_PASSWORD
    })
    assert response.status_code == 200
    login = response.json()["access_token"]
    apartment_response = client.post('/add_apartment/', data=add_apartment_data, headers={"Authorization": f"Bearer {login}"})

    assert apartment_response.status_code == 200
    return response.json()["access_token"]


@pytest.fixture(scope='function')
def add_user_apartment_review_1(add_user_apartment_1, add_user_2, session):
    response_2 = client.post("/login/", data={
        "grant_type": "password",
        "username": TEST_USER_EMAIL + 'test',
        "password": TEST_USER_PASSWORD
    })
    assert response_2.status_code == 200

    response_1 = client.post("/login/", data={
        "grant_type": "password",
        "username": TEST_USER_EMAIL,
        "password": TEST_USER_PASSWORD
    })

    login = response_2.json()["access_token"]
    apartment_id = session.exec(select(Apartment).where(Apartment.user_name == TEST_USER_NAME)).first().id
    review_data["apartment_id"] = apartment_id
    review_response = client.post('/create_review/', headers={"Authorization": f"Bearer {login}"}, data=review_data)
    assert review_response.status_code == 200
    return response_1.json()["access_token"], response_1.json()["access_token"]


# @pytest.fixture(scope='function')
# def add_user_apartment_message_1(add_user_apartment_1, session):
#     user_1 = session.exec(select(User).where(User.email == TEST_USER_EMAIL)).first()
#     apartment_1 = session.exec(select(Apartment).where(Apartment.user_name == user_1.name)).first()
#     message_1 = Message(
#         create_user_id=user_1.id,
#         create_user_email=user_1.email,
#         description=TEST_REVIEW_DESCRIPTION,
#     )
#     session.add(message_1)
#     session.commit()
#     session.close()
#     response = client.post("/login/", data={
#         "grant_type": "password",
#         "username": TEST_USER_EMAIL + 'test',
#         "password": TEST_USER_PASSWORD
#     })
#     assert response.status_code == 200
#     return response.json()["access_token"]
