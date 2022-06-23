from util.errors import CredentialsError
from controller.user_controller.user_creator import UserCreator
from models.db_models import User
from config import CONFIG

from datetime import datetime, timedelta
from controller.user_controller.auth import OAuth2PasswordBearer
from tortoise.exceptions import DoesNotExist
from passlib.hash import bcrypt
from fastapi import Depends, HTTPException, Response
from jose import jwt
from dateutil import parser

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/user/login")


async def create_user(email, password):
    user = await UserCreator(
        email=email,
        password=password,
    )()
    return user


async def verify_password(password: str, password_hash: str):
    return bcrypt.verify(password, password_hash)


async def delete_user(user, password, password_hash):
    if not await verify_password(password, password_hash):
        raise CredentialsError
    
    try:
        await user.delete()
    except DoesNotExist:
        raise HTTPException(status_code=404, detail="USER_DOES_NOT_EXISTS_ERROR")

    return True


async def authenticate_user(email: str, password: str):
    try:
        user = await User.get(email=email)
    except DoesNotExist:
        raise HTTPException(status_code=404, detail="USER_DOES_NOT_EXIST_ERROR")

    if not await verify_password(password, user.password):
        raise CredentialsError

    return await create_access_token(user)


async def create_access_token(user: dict):
    to_ecnode = {
        "email": user.email,
        "password": user.password,
        "expiry": str(datetime.utcnow() + timedelta(minutes = CONFIG.ACCES_TOKEN_EXPIRE_MINUTES)),
        }
    token = jwt.encode(to_ecnode, CONFIG.SECRET_KEY, CONFIG.ALGORITHM)
    return token


async def get_current_user(token: str = Depends(oauth2_scheme)):
    decode_token = jwt.decode(token, CONFIG.SECRET_KEY, CONFIG.ALGORITHM)
    if parser.parse(decode_token["expiry"]) >= datetime.utcnow():
        return await User.get(email=decode_token["email"])
    else:
        raise HTTPException(status_code=401, detail="TOKEN_EXPIRED")
        