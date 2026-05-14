from fastapi.testclient import TestClient
import faker
from app.main import app

client = TestClient(app)
fake = faker.Faker()

client.fake_user_email = fake.email()
client.fake_user_password = fake.password()
client.fake_user_name = fake.first_name()
client.new_user_id = 0
client.auth_token = ""


def test_signup():
    response = client.post("/auth/signup",
                           json={"email": client.fake_user_email,
                                 "password": client.fake_user_password,
                                 "name": client.fake_user_name}
    )
    assert response.status_code == 201
    client.new_user_id = response.json()


def test_bad_signup():
    response = client.post("/auth/signup",
                           json={"email": 'client.fake_user_email',
                                 "password": client.fake_user_password,
                                 "name": client.fake_user_name}
    )
    assert response.status_code == 422


def test_signup_not_unique_email():
    bad_email = fake.email()
    response = client.post("/auth/signup",
                           json={"email": bad_email,
                                 "password": fake.password(),
                                 "name": fake.first_name()}
    )
    assert response.status_code == 201
    response2 = client.post("/auth/signup",
                           json={"email": bad_email,
                                 "password": fake.password(),
                                 "name": fake.first_name()}
                           )
    assert response2.status_code == 422


def test_login():
    response = client.post("/auth/login",
                           data={"username": client.fake_user_email,
                                 "password": client.fake_user_password}
    )
    assert response.status_code == 200
    client.auth_token = response.json()['access_token']


def test_wrong_password():
    response = client.post("/auth/login",
                           data={"username": client.fake_user_email,
                                 "password": fake.password()}
    )
    assert response.status_code == 401


def test_wrong_login():
    response = client.post("/auth/login",
                           data={"username": fake.email(),
                                 "password": client.fake_user_password}
    )
    assert response.status_code == 401


def test_me_auth():
    """
    Тест запроса требующего авторизацию.
    Проверка соответствия информации конкретному залогиненому пользователю.
    :return:
    """
    response = client.get("/users/me", headers={"Authorization": f"Bearer {client.auth_token}"})
    assert response.status_code == 200
    assert response.json()["email"] == client.fake_user_email
