"""роутер для аунтефикации"""
from datetime import timedelta
from fastapi import (APIRouter, status, Depends, HTTPException)
from fastapi.security.oauth2 import OAuth2PasswordRequestForm
from sqlmodel import (Session, select)
from sqlalchemy.exc import IntegrityError

from app.database import get_session
from app.schemas import models, models_validate

from app.scripts import auth_handler
from app.config import settings


router = APIRouter(prefix="/auth", tags=["Безопасность"])

@router.post("/signup", status_code=status.HTTP_201_CREATED,
             response_model=int,
             summary = 'Добавить пользователя')
def create_user(user: models_validate.SignUpUser,
                session: Session = Depends(get_session)):
    new_user = models.User(
        name=user.name,
        email=user.email,
        password=auth_handler.get_password_hash(user.password)
    )
    try:
        session.add(new_user)
        session.commit()
        session.refresh(new_user)

        test_basket = models.Basket(owner_id=new_user.user_id)
        session.add(test_basket)
        session.flush()
        print("b", test_basket.basket_id)
        new_user.own_basket = test_basket
        return new_user.user_id
    except IntegrityError:
        session.rollback()
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail=f"User with email {user.email} already exists"
        )


@router.post("/login", status_code=status.HTTP_200_OK,
             summary = 'Войти в систему')
def user_login(login_attempt_data: OAuth2PasswordRequestForm = Depends(),
               db_session: Session = Depends(get_session)):
    statement = (select(models.User)
                 .where(models.User.email == login_attempt_data.username))
    existing_user = db_session.exec(statement).first()

    if not existing_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"User {login_attempt_data.username} not found"
        )

    if auth_handler.verify_password(
            login_attempt_data.password,
            existing_user.password):
        access_token_expires = timedelta(minutes=settings.access_token_expire_minutes)
        access_token = auth_handler.create_access_token(
            data={"sub": login_attempt_data.username},
            expires_delta=access_token_expires
        )
        return {
            "access_token": access_token,
            "token_type": "bearer"
        }
    else:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Wrong password for user {login_attempt_data.username}"
        )
