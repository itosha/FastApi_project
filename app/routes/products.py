"""роутер для просмотра продуктов, добавления в корзину"""
from typing import Annotated
from fastapi import (APIRouter, status, Depends, HTTPException)
from sqlmodel import (Session, select)
from sqlalchemy.exc import IntegrityError
from app.scripts.auth_handler import get_current_user

from app.database import get_session
from app.schemas.models import (Product, User, Comment)

from app.schemas.models_validate import (PreviewProductList, PreviewProductComm)

router = APIRouter(prefix="/products", tags=["Лента товаров"])


@router.get('/', status_code=status.HTTP_200_OK, summary = 'Лента товаров',
            response_model=PreviewProductList)
def all_products_list(session: Session = Depends(get_session)):
    products = session.exec(select(Product)).all()
    if products is None or len(products) == 0:
        raise HTTPException(
            status_code=status.HTTP_204_NO_CONTENT,
            detail="The products list is empty. Market is close("
        )
    return {"products_list": products}


@router.get('/{product_id}', status_code=status.HTTP_200_OK, summary = 'Детали товара c отзывами',
            response_model=PreviewProductComm)
def product_comm_view(product_id: int, session: Session = Depends(get_session)):
    product = session.get(Product, product_id)
    if product is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Product with id {product_id} does not exist."
        )
    answer = {"comments": []}
    for comm in product.comments:
        answer["comments"].append({"message": comm.message, "author": comm.author.name, "comm_id": comm.comment_id})
    return product.model_dump() | {"seller_name": product.seller.name} | answer


@router.post('/{product_id}', status_code=status.HTTP_201_CREATED,
             summary = 'Добавление отзыва под товаром',
             response_model=Comment)
def add_comm(product_id: int,
             current_user: Annotated[User, Depends(get_current_user)],
             data: str,
             session: Session = Depends(get_session)):
    product = session.get(Product, product_id)
    if product is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Product with {product_id} does not exist."
        )
    com = Comment(message=data, product_id=product_id, author_id=current_user.user_id)
    try:
        session.add(com)
        session.commit()
        session.refresh(com)
    except IntegrityError:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Too long message"
        )
    return com


@router.patch('/{product_id}/{com_id}', status_code=status.HTTP_200_OK,
             summary = 'Редактирование отзыва',
             response_model=Comment)
def rewrite_comm(product_id: int, com_id: int,
             current_user: Annotated[User, Depends(get_current_user)],
             data: str,
             session: Session = Depends(get_session)):
    comm = session.get(Comment, com_id)
    if comm is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Comment with {com_id} does not exist."
        )
    if comm.author_id != current_user.user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"You dont have access to rewrite this comment id: {com_id}."
        )
    if comm.product_id != product_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="The selected comment was not left under the selected product"
        )
    comm.message = data
    session.commit()
    session.refresh(comm)

    return comm


@router.delete('/{product_id}/{com_id}', status_code=status.HTTP_200_OK,
             summary = 'Удаление отзыва',
             response_model=str)
def delete_comm(product_id: int, com_id: int,
             current_user: Annotated[User, Depends(get_current_user)],
             session: Session = Depends(get_session)):
    comm = session.get(Comment, com_id)
    if comm is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Comment with {com_id} does not exist."
        )
    if comm.author_id != current_user.user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"You dont have access to delete this comment id: {com_id}."
        )
    if comm.product_id != product_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="The selected comment was not left under the selected product"
        )
    session.delete(comm)
    session.commit()

    return f'Comment with id {com_id} delete'


@router.get('/to_basket/{product_id}', status_code=status.HTTP_200_OK, summary = 'Детали товара c отзывами')
def product_to_basket(product_id: int, current_user: Annotated[User, Depends(get_current_user)],
                      session: Session = Depends(get_session)):
    product = session.get(Product, product_id)
    if product is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Product with id {id} does not exist."
        )
    print('!', current_user.own_basket.products)
    if product.seller_id == current_user.user_id:
        return 'You can not buy your own products'
    if product not in current_user.own_basket.products:
        current_user.own_basket.products.append(product)
        session.commit()
        session.refresh(current_user)
    else:
        return f'You already have an item in your basket with id {product_id}'
    return f'Product with {product_id} has been added to your basket /users/me/own_basket'
