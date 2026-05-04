from markdown_it.rules_block import table
from pydantic import BaseModel, Field, BeforeValidator, EmailStr
from pydantic_settings import SettingsConfigDict
from typing import Optional, Annotated, TypeAlias, List
from sqlmodel import SQLModel, Field as SQLField, Relationship
from sqlalchemy import UniqueConstraint


def _empty_str_or_none(value: str | None) -> None:
    if value is None or value == "":
        return None
    raise ValueError("Expected empty value")


EmptyStrOrNone: TypeAlias = Annotated[None, BeforeValidator(_empty_str_or_none)]


class User(SQLModel, table=True):
    __tablename__ = 'users'
    __table_args__ = (UniqueConstraint("email"),)
    user_id: int = SQLField(default=None, nullable=False, primary_key=True)
    email: EmailStr = SQLField(nullable=True, unique_items=True)
    password: str | None
    name: str

    own_basket: int = SQLField(foreign_key="basket.basket_id")
    own_products: int = Relationship(back_populates="seller")

    model_config = SettingsConfigDict(
        json_schema_extra = {
            "example": {
                "name": "Иван Иванов",
                "email": "user@example.com",
                "password": "qwerty"
            }
        })


class BasketProductLink(SQLModel, table=True):
    basket_id: int = SQLField(foreign_key="basket.basket_id", primary_key=True)
    product_id: int = SQLField(foreign_key="products.product_id", primary_key=True)


class Product(SQLModel, table=True):
    __tablename__ = 'products'
    product_id: int = SQLField(default=None, nullable=False, primary_key=True)
    product_name: str = Field(description="Название товара", max_length=300)
    price: float = Field(description="Цена за один товар", gt=0)
    amount: int = Field(description="Кол-во товаров в наличии", gt=-1)
    seller_id: int = SQLField(foreign_key="users.user_id")
    seller: User = Relationship(back_populates="own_products")
    baskets: List["Basket"] = Relationship(back_populates="products", link_model=BasketProductLink)


class Basket(SQLModel, table=True):
    __tablename__ = 'basket'
    basket_id: int = SQLField(default=None, nullable=False, primary_key=True)
    owner: int = SQLField(foreign_key="users.user_id")
    products: List[Product] = Relationship(back_populates="baskets", link_model=BasketProductLink)
