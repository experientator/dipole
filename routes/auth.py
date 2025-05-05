from fastapi import APIRouter, status, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlmodel import Session, select
from db.session import get_session
from schemas import tasks as schema_task
from schemas.models import User
from sqlalchemy.exc import IntegrityError
from psycopg2.errors import UniqueViolation
from auth.auth_handler import (get_password_hash,
                               create_access_token, verify_password)

router = APIRouter(prefix="/auth", tags=["Безопасность"])

@router.post("/signup", status_code=status.HTTP_201_CREATED,
             summary = 'Добавить пользователя')
def create_user(user: schema_task.User,
                session: Session = Depends(get_session)):
    new_user = User(name=user.name,
                    email=user.email,
                    password=get_password_hash(user.password))
    try:
        session.add(new_user)
        session.commit()
        session.refresh(new_user)
        return {"name": user.name,
                "email": user.email}
    except IntegrityError as e:
        assert isinstance(e.orig, UniqueViolation)
        raise HTTPException(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        detail=f"User with email {user.email} already exists"
    )
    
@router.post("/login", status_code=status.HTTP_200_OK)
def user_login(login_attempt_data: OAuth2PasswordRequestForm = Depends(),
               db_session: Session = Depends(get_session)):
    statement = (select(User)
                 .where(User.name == login_attempt_data.username))
    existing_user = db_session.exec(statement).first()
    if not existing_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"User {login_attempt_data.username} not found"
        )
    if verify_password(
            login_attempt_data.password,
            existing_user.password):
        access_token = create_access_token(
            existing_user.user_id)
        return {
            "access_token": access_token,
            "token_type": "bearer"
        }
    else:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Wrong password for user {login_attempt_data.username}"
        )