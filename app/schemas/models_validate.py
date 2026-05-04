from pydantic import BaseModel, Field, BeforeValidator, EmailStr
from pydantic_settings import SettingsConfigDict
from typing import Optional, Annotated, TypeAlias, List


class PreviewUser(BaseModel):
    email: EmailStr
    name: str


class PreviewComm(BaseModel):
    author: str
    message: str
    comm_id: int


class PreviewProduct(BaseModel):
    product_name: str = Field(description="Название товара", max_length=300)
    price: float = Field(description="Цена за один товар", gt=0)
    amount: int = Field(description="Кол-во товаров в наличии", gt=-1)
    seller_id: int
    product_id: int


class PreviewProductComm(PreviewProduct):
    seller_name: str
    comments: List[PreviewComm]


class PreviewProductList(BaseModel):
    products_list: List[PreviewProduct]