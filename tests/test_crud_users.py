# tests/test_crud_users.py
from app import crud


def test_create_user_and_list_users(db_session):
    user_data = {
        "name": "test_user",
        "email": "test@example.com",
        # если у тебя есть обязательные поля — добавь их сюда
        # "password": "123" и т.п.
    }

    created = crud.create_user(db_session, user_data)
    assert created.id is not None
    assert created.email == "test@example.com"

    users = crud.get_users(db_session)
    assert len(users) == 1
    assert users[0].id == created.id
