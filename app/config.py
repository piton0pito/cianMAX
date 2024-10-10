import os
from dotenv import load_dotenv

load_dotenv()

HOST = os.environ.get("MAIL_HOST")
USERNAME = os.environ.get("MAIL_USERNAME")
PASSWORD = os.environ.get("MAIL_PASSWORD")
PORT = os.environ.get("MAIL_PORT", 465)
# https://ethereal.email/create

SECRET_KEY = os.environ.get("SECRET_KEY")
ALGORITHM = os.environ.get("ALGORITHM")

PASS_ADMIN = os.environ.get("PASS_ADMIN")
EMAIL_ADMIN = os.environ.get("EMAIL_ADMIN")

TEST_USER_EMAIL = os.environ.get("TEST_USER_EMAIL")
TEST_USER_PHONE = os.environ.get("TEST_USER_PHONE")
TEST_USER_NAME = os.environ.get("TEST_USER_NAME")
TEST_USER_LICENSE = os.environ.get("TEST_USER_LICENSE")
TEST_USER_PASSWORD = os.environ.get("TEST_USER_PASSWORD")

TEST_APARTMENT_ADDRESS = os.environ.get("TEST_APARTMENT_ADDRESS")
TEST_APARTMENT_CITY = os.environ.get("TEST_APARTMENT_CITY")
TEST_APARTMENT_TYPE = os.environ.get("TEST_APARTMENT_TYPE")
TEST_APARTMENT_M = os.environ.get("TEST_APARTMENT_M")
TEST_APARTMENT_PRISE = os.environ.get("TEST_APARTMENT_PRISE")
TEST_APARTMENT_DESCRIPTION = os.environ.get("TEST_APARTMENT_DESCRIPTION")

TEST_REVIEW_DESCRIPTION = os.environ.get("TEST_REVIEW_DESCRIPTION")
TEST_REVIEW_STARS = os.environ.get("TEST_REVIEW_STARS")
