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

get_apartment_data = {
  "city": "None",
  "type": "None",
  "from_m": -1,
  "before_m": -1,
  "from_prise": -1,
  "before_prise": -1,
  "offset": 0,
  "limit": 10
}

add_apartment_data = {
  "city": "gg",
  "address": "gg",
  "type": "g",
  "m": 52,
  "prise": 52,
  "description": "d"
}

update_description_data = {
  "id": 0,
  "description": "string"
}

review_data = {
  "apartment_id": 0,
  "stars": 2,
  "description": "description",
  "anonim": False
}

add_message_data = {
  "apartment_id": 0,
  "phone": True,
  "description": "description"
}
