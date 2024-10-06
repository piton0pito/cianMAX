import os
import urllib
import uuid
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import smtplib
from typing import List

import openpyxl
from PIL.Image import Image

from app.config import HOST, USERNAME, PASSWORD, PORT

from random import randint
from fastapi import Depends, UploadFile

from fastapi import HTTPException
from datetime import datetime, timedelta

from app.config import SECRET_KEY, ALGORITHM
from fastapi.security import OAuth2PasswordBearer
from jwt import PyJWTError, encode, decode
from hashlib import sha256
from sqlmodel import select, Session

from app.db import get_session
from app.models import User

# SECRET_KEY = "macsim_ebanat"
# ALGORITHM = "HS256"

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

credentials_error = HTTPException(
    status_code=401,
    detail="Could not validate credentials",
    headers={"WWW-Authenticate": "Bearer"}, )


def create_access_token(data: dict, exp: timedelta = None):
    to_encode = data.copy()
    if exp:
        expire = datetime.utcnow() + exp
    else:
        expire = datetime.utcnow() + timedelta(minutes=60)
    to_encode.update({"exp": expire})
    encoded_jwt = encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def verify_access_token(token: str = Depends(oauth2_scheme), session: Session = Depends(get_session)):
    try:
        payload = decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_error
        user = session.exec(select(User).where(User.id == user_id)).first()
        if user is None:
            raise credentials_error
        return user
    except PyJWTError:
        raise credentials_error


def hash_password(password: str):
    return sha256(password.encode()).hexdigest()


def send_mail(reception_email: str, code: str):
    # create message object instance
    msg = MIMEMultipart()

    # set up the parameters of the message
    password = PASSWORD
    msg['From'] = USERNAME
    msg['To'] = reception_email
    msg['Subject'] = "Reset password"

    # add in the message body
    msg.attach(MIMEText(code, 'plain'))

    # create server
    server = smtplib.SMTP(f'{HOST}: {PORT}')
    server.starttls()
    server.login(msg['From'], password)
    # send the message via the server.
    server.sendmail(msg['From'], msg['To'], msg.as_string())
    server.quit()


async def get_meme():
    urllib.request.urlretrieve('https://img.randme.me/', "meme.jpg")


def gen_res_key():
    num = str(randint(1, 999999))
    return ('0' * (6 - len(num))) + num


def get_delta_time(date_1: datetime, date_2: datetime):
    time_difference = date_2 - date_1
    minutes_difference = time_difference.seconds / 60 + time_difference.microseconds / 1000000 / 60
    return int(minutes_difference)


def get_xlsx(users, file_name):
    # Create a workbook and select the active sheet
    workbook = openpyxl.Workbook()
    sheet = workbook.active
    # Write the headers
    headers = ['id', 'date_reg', 'email', 'role', 'name']
    sheet.append(headers)
    # Write the users
    for user in users:
        user = dict(user)
        row = [user[header] for header in headers]
        sheet.append(row)
    # Save the workbook
    workbook.save(file_name)


async def process_images(images: list[UploadFile], target_dir: str, target_name: str) -> list[str]:
    saved_images = []
    for i, image in enumerate(images):
        # Check if the image is a JPEG
        if image.content_type != 'image/jpeg':
            raise ValueError(f"Image {image.filename} is not a JPEG")

        # Check if the image size is not more than 5MB
        if image.size > 5 * 1024 * 1024:
            raise ValueError(f"Image {image.filename} is too large (max 5MB)")

        # Generate a unique filename
        filename = f"{target_name}_{i}.jpg"

        # Save the image to the target directory
        image_path = os.path.join(target_dir, filename)
        with open(image_path, 'wb') as f:
            f.write(await image.read())

        saved_images.append(image_path)

    return saved_images


async def get_image_paths(apartment_id: int) -> List[str]:
    directory = '../media'
    images_path = []
    for filename in os.listdir(directory):
        if filename.startswith(f"{apartment_id}_") and filename.endswith(".jpg"):
            foto_id = filename.split("_")[1].split(".")[0]
            images_path.append(os.path.join(directory, filename))
    return images_path
