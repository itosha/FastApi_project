from fastapi import APIRouter, status, Depends, HTTPException

from app.schemas.models_validate import PreviewUserList, PreviewProductList
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


@router.get('/me', status_code=status.HTTP_200_OK,
            summary = 'Ваши данные',
            response_model=PreviewProductList)
def own_data(current_user: Annotated[User, Depends(get_current_user)],
             session: Session = Depends(get_session)):
    profile = current_user.model_dump()
    del profile['password']

    return profile


@router.patch('/me', status_code=status.HTTP_200_OK,
            summary='Ваши данные',
            response_model=PreviewProductList)
def own_data(new_name: str, current_user: Annotated[User, Depends(get_current_user)],
             session: Session = Depends(get_session)):
    current_user.name = new_name
    session.commit()
    session.refresh(current_user)

    return f'your nickname have been updated to {new_name}'


@router.get('/me/own_products', status_code=status.HTTP_200_OK,
            summary = 'Список ваших товаров',
            response_model=PreviewProductList)
def own_products(current_user: Annotated[User, Depends(get_current_user)],
             session: Session = Depends(get_session)):
    own_list = current_user.own_products
    if own_list is None or len(own_list) == 0:
        raise HTTPException(
            status_code=status.HTTP_204_NO_CONTENT,
            detail=f"You haven't put anything up for sale yet"
        )
    arr = sorted(own_list, key=lambda a: a.amount)
    return {"products_list": arr}


@router.get('/me/own_basket', status_code=status.HTTP_200_OK,
            summary = 'Содержимое вашей корзины')
def own_basket(current_user: Annotated[User, Depends(get_current_user)],
             session: Session = Depends(get_session)):
    own_list = current_user.own_basket.products
    if own_list is None or len(own_list) == 0:
        raise HTTPException(
            status_code=status.HTTP_204_NO_CONTENT,
            detail=f"You haven't put anything on your basket"
        )
    arr = sorted(own_list, key=lambda a: a.price)
    return {"products_list": arr}


@router.post('/me/own_basket/buy', status_code=status.HTTP_200_OK,
            summary = 'Покупка')
def own_basket_buy(product_id: int, num_of_product: int,
               current_user: Annotated[User, Depends(get_current_user)],
             session: Session = Depends(get_session)):
    product = session.get(Product, product_id)
    if product is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Such Product with id {id} does not exist at all."
        )
    elif num_of_product <= 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Incorrect number of items to purchase {num_of_product}"
        )
    elif product not in current_user.own_basket.products:
        return f'Please add the item to your basket first /products/to_basket/{product_id}'
    elif num_of_product > product.amount:
        return f'The seller does not have enough goods {num_of_product}'
    sum = num_of_product * product.price
    if sum > current_user.wallet:
        return f'Недостаточно средств на балансе. Нужно: {sum}. В наличии: {current_user.wallet}'
    else:
        current_user.wallet -= sum
        product.seller.wallet += sum  # 5 сервиса чисто на воздухе работает - комиссию не берет
        product.seller.num_of_deals += 1
        product.amount -= num_of_product
        current_user.own_basket.products.remove(product)
        session.commit()
        session.refresh(current_user)
        session.refresh(product)
    return f'Успешная покупка'


@router.patch('/me/wallet', status_code=status.HTTP_200_OK,
            summary = 'Пополнение или вывод средств с баланса')
def own_wallet(money: float,
               current_user: Annotated[User, Depends(get_current_user)],
             session: Session = Depends(get_session)):
    res = current_user.wallet + money
    if money == 0.0:
        return f'Your balance has not changed'
    elif money < 0:
        if res < 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"You do not have enough balance {current_user.wallet} to withdraw this amount of money {money}"
            )
        else:
            current_user.wallet = res
            session.commit()
            session.refresh(current_user)
            return f'Вы вывели {money}. На Вашем балансе осталось {res}'
    else:
        current_user.wallet = res
        session.commit()
        session.refresh(current_user)
        return f'Вы положили на баланс {money}. На Вашем балансе теперь {res}'



