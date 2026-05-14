"""db_init"""
from sqlmodel import create_engine, Session, select, SQLModel
from passlib.context import CryptContext
from app.schemas.models import User, Product, Basket, Comment

DATABASE_URL = "sqlite:///db.splite"

engine = create_engine(DATABASE_URL, echo=True)

def get_session():
    with Session(engine) as session:
        yield session

def init_database():
    SQLModel.metadata.create_all(engine)

    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

    with Session(engine) as session:
        statement = select(User).where(User.name == "seller_gold")
        existing_user = session.exec(statement).first()

        id_1 = 0

        if not existing_user:
            test_user = User(
                name="seller_gold",
                email="gold@example.com",
                password=pwd_context.hash("admin")
            )
            session.add(test_user)
            session.flush()

            test_basket = Basket(owner_id=test_user.user_id)
            session.add(test_basket)
            session.flush()

            test_user.own_basket = test_basket

            # 3. Создаем продукты и привязываем их к продавцу
            # Благодаря Relationship, мы можем просто добавить их в список
            item1 = Product(product_name="Ноутбук", price=50000.0, amount=10, seller_id=test_user.user_id)
            item2 = Product(product_name="Мышь", price=1500.0, amount=18, seller_id=test_user.user_id)
            session.add(item1)
            session.add(item2)
            session.flush()

            id_1 = item1.product_id

            test_user.own_products = [item1, item2]

            session.commit()

        statement = select(User).where(User.name == "Vasek")
        existing_user = session.exec(statement).first()

        if not existing_user:
            test_user2 = User(
                name="Vasek",
                email="vasek@example.com",
                password=pwd_context.hash("12345")
            )
            session.add(test_user2)
            session.flush()

            test_basket2 = Basket(owner_id=test_user2.user_id)
            session.add(test_basket2)
            session.flush()

            test_user2.own_basket = test_basket2

            com = Comment(message="Не ну а что. Ноут норм.", author_id=test_user2.user_id, product_id=id_1)
            session.add(com)
            session.commit()
