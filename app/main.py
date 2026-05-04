"""main"""
from itertools import product

from fastapi import FastAPI
from app.routes import auth, products

from contextlib import asynccontextmanager
from app.database import init_database


@asynccontextmanager
async def lifespan(app: FastAPI):
   init_database()
   yield

app = FastAPI(
    lifespan=lifespan,
    title="Модель марткетплейса",
    description="Учебный проект на фреймворке FastAPI.",
    version="0.0.1"
)

app.include_router(auth.router)
app.include_router(products.router)
