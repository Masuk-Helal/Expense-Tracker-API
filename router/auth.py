from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, ConfigDict, EmailStr
from sqlalchemy.orm import Session
from datetime import timedelta, datetime, timezone
from typing import Annotated
from database import SessionLocal
from models import Users
from passlib.context import CryptContext
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from jose import jwt, JWTError
import os

router = APIRouter(prefix='/auth', tags=['auth'])

bcrypt_context = CryptContext(schemes=['bcrypt'], deprecated='auto')
OAuth2_bearer = OAuth2PasswordBearer(tokenUrl='auth/login')

SECRET_KEY = os.getenv('SECRET_KEY', '86746eeb8285ca279c6251e0bd83cdd50c88027b934a93f19d8b9af782139516')
ALGORITHM = 'HS256'


class CreateUser(BaseModel):
    username: str
    email: EmailStr
    password: str


class UserOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    username: str
    email: str


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


db_dependency = Annotated[Session, Depends(get_db)]


def authenticate_user(username, password, db):
    user = db.query(Users).filter(Users.username == username).first()
    if user is None:
        return False
    if not bcrypt_context.verify(password, user.hashed_password):
        return False
    return user


def create_access_token(username: str, user_id: int, expires_delta: timedelta):
    encode = {'sub': username, 'id': user_id}
    expires = datetime.now(timezone.utc) + expires_delta
    encode.update({'exp': expires})
    return jwt.encode(encode, SECRET_KEY, algorithm=ALGORITHM)


def get_current_user(token: Annotated[str, Depends(OAuth2_bearer)]):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get('sub')
        user_id: int = payload.get('id')
        if username is None or user_id is None:
            raise HTTPException(status_code=401, detail='Could not validate user')
        return {'username': username, 'id': user_id}
    except JWTError:
        raise HTTPException(status_code=401, detail='Could not validate user')


user_dependency = Annotated[dict, Depends(get_current_user)]


@router.post('/register', status_code=201, response_model=UserOut)
def register_user(db: db_dependency, new_user: CreateUser):

    existing_user = db.query(Users).filter(
        (Users.username == new_user.username) | (Users.email == new_user.email)
    ).first()
    if existing_user is not None:
        raise HTTPException(status_code=400, detail='Username or email already registered')

    user_model = Users(
        username=new_user.username,
        email=new_user.email,
        hashed_password=bcrypt_context.hash(new_user.password),
    )

    db.add(user_model)
    db.commit()
    db.refresh(user_model)

    return user_model


@router.post('/login')
def login_user(db: db_dependency, form_data: Annotated[OAuth2PasswordRequestForm, Depends()]):

    user = authenticate_user(form_data.username, form_data.password, db)
    if not user:
        raise HTTPException(status_code=401, detail='Failed Authentication')

    token = create_access_token(user.username, user.id, timedelta(minutes=30))
    return {'access_token': token, 'token_type': 'bearer'}
