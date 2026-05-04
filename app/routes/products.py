from fastapi import APIRouter, status, HTTPException

router = APIRouter(prefix="/products", tags=["Лента товаров"])


@router.get('/', status_code=status.HTTP_200_OK, summary = 'Лента товаров')
def all_products_list():
    ...

