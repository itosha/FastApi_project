"""db_init"""
from sqlmodel import create_engine, Session, SQLModel


DATABASE_URL = "sqlite:///db.splite:shared?mode=memory&cache=shared"

engine = create_engine(DATABASE_URL, echo=True)

def get_session():
    with Session(engine) as session:
        yield session

def init_database():
    SQLModel.metadata.create_all(engine)
