from markdown_it.rules_block import table
from pydantic import BaseModel, Field, BeforeValidator, EmailStr
from pydantic_settings import SettingsConfigDict
from typing import Optional, Annotated, TypeAlias
from sqlmodel import SQLModel, Field as SQLField
from sqlalchemy import UniqueConstraint


def _empty_str_or_none(value: str | None) -> None:
    if value is None or value == "":
        return None
    raise ValueError("Expected empty value")


EmptyStrOrNone: TypeAlias = Annotated[None, BeforeValidator(_empty_str_or_none)]


class User(SQLModel, table=True):
    __table_args__ = (UniqueConstraint("email"),)
    user_id: int = SQLField(default=None, nullable=False, primary_key=True)
    email: EmailStr = SQLField(nullable=True, unique_items=True)
    password: str | None
    name: str

    model_config = SettingsConfigDict(
        json_schema_extra = {
            "example": {
                "name": "Иван Иванов",
                "email": "user@example.com",
                "password": "qwerty"
            }
        })


class Product(BaseModel):
    product_name: str = Field(description="Название товара", max_length=300)
    price: float = Field(description="Цена за один товар", gt=0)
    amount: int = Field(description="Кол-во товаров в наличии", gt=0)

