from markdown_it.rules_block import table
from pydantic import BaseModel, Field, BeforeValidator, EmailStr
from pydantic_settings import SettingsConfigDict
from typing import Optional, Annotated, TypeAlias
from sqlmodel import SQLModel, Field as SQLField


def _empty_str_or_none(value: str | None) -> None:
    if value is None or value == "":
        return None
    raise ValueError("Expected empty value")


EmptyStrOrNone: TypeAlias = Annotated[None, BeforeValidator(_empty_str_or_none)]


class Product(BaseModel, table=True):
    product_name: str = Field(description="Название товара", max_length=300)
    price: float = Field(description="Цена за один товар", gt=0)
    amount: int = Field(description="Кол-во товаров в наличии", gt=0)

