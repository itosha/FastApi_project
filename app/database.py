"""db_init"""
from sqlmodel import create_engine, Session, SQLModel
from app.schemas.models import User, Product, Basket

DATABASE_URL = "sqlite:///db.splite"

engine = create_engine(DATABASE_URL, echo=True)

def get_session():
    with Session(engine) as session:
        yield session

def init_database():
    SQLModel.metadata.create_all(engine)

    from passlib.context import CryptContext
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

    with Session(engine) as session:
        test_user = User(
            name="seller_gold",
            email="gold@example.com",
            password=pwd_context.hash("admin")
        )
        session.add(test_user)
        session.flush()
        print('u', test_user.user_id)

        test_basket = Basket(owner_id=test_user.user_id)
        session.add(test_basket)
        # session.flush()
        print("b", test_basket.basket_id)
        test_user.own_basket = test_basket.basket_id

        # 3. Создаем продукты и привязываем их к продавцу
        # Благодаря Relationship, мы можем просто добавить их в список
        item1 = Product(product_name="Ноутбук", price=50000.0, amount=10, seller_id=test_user.user_id)
        item2 = Product(product_name="Мышь", price=1500.0, amount=18, seller_id=test_user.user_id)
        session.add(item1)
        session.add(item2)
        session.flush()

        test_user.own_products = [item1, item2]

        session.commit()

