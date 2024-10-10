import pytest
from fastapi.testclient import TestClient
from sqlmodel import select

from app.config import TEST_USER_NAME
from app.main import app
from app.models import Apartment
from test.conftest import client, add_test_user_1, add_test_user_2, add_user_apartment_1, add_user_apartment_2
from test.data_for_test import get_apartment_data, add_apartment_data, update_description_data


def test_get_apartments(add_test_user_1, clear_database):
    response = client.post("/get_apartments/", json=get_apartment_data)
    assert response.status_code == 200


def test_get_apartment(add_user_apartment_1, clear_database):
    user_1 = add_user_apartment_1
    response = client.post("/get_apartment_data/1", headers={"Authorization": f"Bearer {user_1}"})
    assert response.status_code == 200

    response = client.post("/get_apartment_data/100", headers={"Authorization": f"Bearer {user_1}"})
    assert response.status_code == 404


def test_get_apartment_photo_ids(add_user_apartment_1, clear_database):
    user_1 = add_user_apartment_1
    response = client.get("/get_apartment_photo_ids/1", headers={"Authorization": f"Bearer {user_1}"})
    assert response.status_code == 200

    response = client.get("/get_apartment_photo_ids/100", headers={"Authorization": f"Bearer {user_1}"})
    assert response.status_code == 404


def test_add_apartment(add_test_user_1, clear_database):
    user_1 = add_test_user_1
    response = client.post("/add_apartment/", json=add_apartment_data,
                           headers={"Authorization": f"Bearer {user_1}"})
    assert response.status_code == 201
    # Test error response for invalid input
    response = client.post("/add_apartment/", headers={"Authorization": f"Bearer {user_1}"})
    assert response.status_code == 422


# def test_inactive_apartment(add_user_apartment_1, session):
#     user_1 = add_user_apartment_1
#     apartment_id = session.exec(select(Apartment).where(Apartment.user_name == TEST_USER_NAME)).first()
#     print(apartment_id.id)
#     print(user_1)
#     response = client.put(f"/inactive_apartment/{apartment_id.id}", headers={"Authorization": f"Bearer {user_1}"})
#     print(response)
#     assert response.status_code == 200
#     # Test error response for non-existent apartment
#     response = client.put("/inactive_apartment/100", headers={"Authorization": f"Bearer {user_1}"})
#     assert response.status_code == 404


def test_user_apartment(add_user_apartment_1, clear_database):
    user_1 = add_user_apartment_1
    response = client.get("/user_apartment/1", headers={"Authorization": f"Bearer {user_1}"})
    assert response.status_code == 200
    # Test error response for non-existent user
    response = client.get("/user_apartment/100", headers={"Authorization": f"Bearer {user_1}"})
    assert response.status_code == 404
