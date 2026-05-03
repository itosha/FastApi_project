"""main"""
from fastapi import FastAPI

from contextlib import asynccontextmanager  # Uncomment if you need to create tables on app start >
from database import init_database


@asynccontextmanager
async def lifespan(app: FastAPI):
   init_database()
   yield  # <<< Uncomment if you need to create tables on app start

app = FastAPI(
    lifespan=lifespan,  # Uncomment if you need to create tables on app start
    title="Модель марткетплейса",
    description="Учебный проект на фреймворке FastAPI.",
    version="0.0.1"
)

# app.include_router(task.router)
