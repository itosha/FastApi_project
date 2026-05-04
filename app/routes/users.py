from fastapi import APIRouter, status, Depends, HTTPException

from app.schemas.models_validate import PreviewUserList
from app.scripts.auth_handler import get_current_user
from typing import Annotated
from sqlmodel import Session, select
from app.database import get_session
from app.schemas.models import Product, User, Comment

router = APIRouter(prefix="/users", tags=["Просмотр пользователей и работа с личным кабинетом"])


@router.get('/', status_code=status.HTTP_200_OK,
            summary = 'Список всех продавцов (только те у кого есть лоты)',
            response_model=PreviewUserList)
def all_sellers_list(session: Session = Depends(get_session)):
    users = session.exec(select(User)).all()
    if users is None or len(users) == 0:
        raise HTTPException(
            status_code=status.HTTP_204_NO_CONTENT,
            detail=f"The products list is empty. Market is close("
        )
    arr = []
    for u in users:
        if len(u.own_products) > 0:
            res = u.model_dump()
            del res['password']
            arr.append(res)
    print(arr)
    arr = sorted(arr, key=lambda a: a['num_of_deals'])
    return {"user_list": arr}
