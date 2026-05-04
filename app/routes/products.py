from fastapi import APIRouter, status, Depends, HTTPException
from sqlmodel import Session, select
from app.database import get_session
from app.schemas import models
from app.schemas.models import Product

from app.schemas.models_validate import PreviewProductList, PreviewProductComm

router = APIRouter(prefix="/products", tags=["Лента товаров"])


@router.get('/', status_code=status.HTTP_200_OK, summary = 'Лента товаров',
            response_model=PreviewProductList)
def all_products_list(session: Session = Depends(get_session)):
    products = session.exec(select(models.Product)).all()
    if products is None or len(products) == 0:
        raise HTTPException(
            status_code=status.HTTP_204_NO_CONTENT,
            detail=f"The products list is empty. Market is close("
        )
    return {"products_list": products}


@router.get('/{id}', status_code=status.HTTP_200_OK, summary = 'Детали товара c отзывами',
            response_model=PreviewProductComm)
def all_products_list(id: int, session: Session = Depends(get_session)):
    product = session.get(Product, id)
    if product is None:
        raise HTTPException(
            status_code=status.HTTP_204_NO_CONTENT,
            detail=f"Product with {id} does not exist."
        )
    answer = {"comments": []}
    for comm in product.comments:
        answer["comments"].append({"message": comm.message, "author": comm.author.name})
    return product.model_dump() | {"seller_name": product.seller.name} | answer
