from app.config import TEST_USER_EMAIL, TEST_USER_PHONE, TEST_USER_NAME, TEST_USER_PASSWORD

reg_user_data = {
    "email": TEST_USER_EMAIL,
    "phone": TEST_USER_PHONE,
    "name": TEST_USER_NAME,
    "password": TEST_USER_PASSWORD,
    "complete_password": TEST_USER_PASSWORD
}

login_user_data = {
    "grant_type": "password",
    "username": TEST_USER_EMAIL,
    "password": TEST_USER_PASSWORD
}

update_user_data = {
    "email": TEST_USER_EMAIL + 'test',
    "password": TEST_USER_PASSWORD + 'test',
    "complete_password": TEST_USER_PASSWORD + 'test'
}

create_new_password_data = {
    "email": TEST_USER_EMAIL,
    "code": "000000",
    "password": TEST_USER_PASSWORD + 'test',
    "complete_password": TEST_USER_PASSWORD + 'test'
}

email_data = {"email": TEST_USER_EMAIL}

