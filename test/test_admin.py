from app.config import EMAIL_ADMIN
from test.conftest import client


def test_create_first_admin(clear_database):
    response = client.post('/admin/create_first_admin/')
    assert response.status_code == 201
    response = client.post('/admin/create_first_admin/')
    assert response.status_code == 400


def test_get_all_user(add_test_admin_1, add_test_user_1, clear_database):
    response = client.get('/admin/get_all_user/', headers={"Authorization": f"Bearer {add_test_admin_1}"})
    assert response.status_code == 200
    assert response.json()[0]["id"] == 1
    assert response.json()[0]["email"] == EMAIL_ADMIN

    response = client.get('/admin/get_all_user/', headers={"Authorization": f"Bearer {add_test_user_1}"})
    assert response.status_code == 403


def test_get_user_xlsx(add_test_admin_1, add_test_user_2, clear_database):
    response = client.get('/admin/get_user/xlsx', headers={"Authorization": f"Bearer {add_test_admin_1}"})
    assert response.status_code == 200
    assert response.headers["content-type"] == "multipart/form-data"
    assert response.headers["content-disposition"] == 'attachment; filename="users.xlsx"'

    response = client.get('/admin/get_user/xlsx', headers={"Authorization": f"Bearer {add_test_user_2}"})
    assert response.status_code == 403


def test_BAN_user(add_test_admin_1, add_test_user_1, clear_database):
    response = client.put('/admin/BAN_user/2', headers={"Authorization": f"Bearer {add_test_admin_1}"})
    assert response.status_code == 200
    response = client.get('/admin/get_all_user/', headers={"Authorization": f"Bearer {add_test_admin_1}"})
    assert response.status_code == 200
    assert response.json()[1]["id"] == 2
    assert response.json()[1]["role"] == "BAN"

    response = client.put('/admin/BAN_user/2', headers={"Authorization": f"Bearer {add_test_admin_1}"})
    assert response.status_code == 400
    assert response.json()["detail"] == 'The user has already been blocked'

    response = client.put('/admin/BAN_user/9999', headers={"Authorization": f"Bearer {add_test_admin_1}"})
    assert response.status_code == 404
    assert response.json()["detail"] == 'User not found'

    response = client.put('/admin/BAN_user/2', headers={"Authorization": f"Bearer {add_test_user_1}"})
    assert response.status_code == 403


def test_un_BAN_user(add_test_admin_1, add_test_user_1, clear_database):
    response = client.put('/admin/BAN_user/2', headers={"Authorization": f"Bearer {add_test_admin_1}"})
    assert response.status_code == 200
    response = client.put('/admin/un_BAN_user/2', headers={"Authorization": f"Bearer {add_test_admin_1}"})
    assert response.status_code == 200
    response = client.get('/admin/get_all_user/', headers={"Authorization": f"Bearer {add_test_admin_1}"})
    assert response.status_code == 200
    assert response.json()[1]["id"] == 2
    assert response.json()[1]["role"] == "user"

    response = client.put('/admin/un_BAN_user/2', headers={"Authorization": f"Bearer {add_test_admin_1}"})
    assert response.status_code == 400
    assert response.json()["detail"] == 'The user is not blocked'

    response = client.put('/admin/un_BAN_user/9999', headers={"Authorization": f"Bearer {add_test_admin_1}"})
    assert response.status_code == 404
    assert response.json()["detail"] == 'User not found'

    response = client.put('/admin/un_BAN_user/2', headers={"Authorization": f"Bearer {add_test_user_1}"})
    assert response.status_code == 403


def test_make_super_user(add_test_admin_1, add_test_user_1, clear_database):
    response = client.put('/admin/make_super_user/2', headers={"Authorization": f"Bearer {add_test_admin_1}"})
    assert response.status_code == 200
    response = client.get('/admin/get_all_user/', headers={"Authorization": f"Bearer {add_test_admin_1}"})
    assert response.status_code == 200
    assert response.json()[1]["id"] == 2
    assert response.json()[1]["role"] == "super_user"

    response = client.put('/admin/make_super_user/2', headers={"Authorization": f"Bearer {add_test_admin_1}"})
    assert response.status_code == 400
    assert response.json()["detail"] == "The user is already a super user"

    response = client.put('/admin/BAN_user/2', headers={"Authorization": f"Bearer {add_test_admin_1}"})
    assert response.status_code == 200
    response = client.put('/admin/make_super_user/2', headers={"Authorization": f"Bearer {add_test_admin_1}"})
    assert response.status_code == 400
    assert response.json()["detail"] == "The user has already been blocked"

    response = client.put('/admin/make_super_user/9999', headers={"Authorization": f"Bearer {add_test_admin_1}"})
    assert response.status_code == 404
    assert response.json()["detail"] == 'User not found'

    response = client.put('/admin/make_super_user/2', headers={"Authorization": f"Bearer {add_test_user_1}"})
    assert response.status_code == 403


def test_un_make_super_user(add_test_admin_1, add_test_admin_2, add_test_user_1, clear_database):
    response = client.put('/admin/un_make_super_user/2', headers={"Authorization": f"Bearer {add_test_admin_1}"})
    assert response.status_code == 200
    response = client.get('/admin/get_all_user/', headers={"Authorization": f"Bearer {add_test_admin_1}"})
    assert response.status_code == 200
    assert response.json()[1]["id"] == 2
    assert response.json()[1]["role"] == "user"

    response = client.put('/admin/un_make_super_user/2', headers={"Authorization": f"Bearer {add_test_admin_1}"})
    assert response.status_code == 400
    assert response.json()["detail"] == "The user is not a super user"

    response = client.put('/admin/un_make_super_user/9999', headers={"Authorization": f"Bearer {add_test_admin_1}"})
    assert response.status_code == 404
    assert response.json()["detail"] == 'User not found'

    response = client.put('/admin/un_make_super_user/2', headers={"Authorization": f"Bearer {add_test_user_1}"})
    assert response.status_code == 403