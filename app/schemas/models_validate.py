from pydantic import BaseModel, Field, BeforeValidator, EmailStr
from pydantic_settings import SettingsConfigDict
from typing import Optional, Annotated, TypeAlias, List


class PreviewUser(BaseModel):
    email: EmailStr
    name: str


class PreviewProduct(BaseModel):
    product_name: str = Field(description="Название товара", max_length=300)
    price: float = Field(description="Цена за один товар", gt=0)
    amount: int = Field(description="Кол-во товаров в наличии", gt=-1)
    seller: PreviewUser


class PreviewProductList(BaseModel):
    products: List[PreviewProduct]