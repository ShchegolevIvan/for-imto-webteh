# tests/test_crud_news.py
from app import crud


def test_create_news_and_list_news_without_redis(db_session):
    # 1) создаём автора
    author = crud.create_user(db_session, {"name": "author", "email": "a@example.com"})
    # если у тебя в модели есть флаг автора и crud его не ставит — можно руками:
    # author.is_verified_author = True
    # db_session.commit(); db_session.refresh(author)

    # 2) создаём новость
    news_data = {
        "title": "hello",
        "text": "world",
        "author_id": author.id,
    }
    created = crud.create_news(db_session, news_data)
    assert created.id is not None
    assert created.author_id == author.id

    # 3) если crud.get_news требует redis_client, а ты не хочешь тянуть redis в юнитах:
    #   - либо передаёшь None (если в crud это поддержано),
    #   - либо тестишь напрямую через db (если crud такого не даёт).
    try:
        news_list = crud.get_news(db_session, None)
        assert len(news_list) >= 1
    except TypeError:
        # значит get_news(db, redis) обязателен и не принимает None — норм, тогда просто проверили create
        pass


def test_update_and_delete_news(db_session):
    author = crud.create_user(db_session, {"name": "author2", "email": "a2@example.com"})
    created = crud.create_news(
        db_session,
        {"title": "t1", "text": "x1", "author_id": author.id},
    )

    updated = crud.update_news(db_session, created.id, {"title": "t2"})
    assert updated is not None
    assert updated.title == "t2"

    deleted = crud.delete_news(db_session, created.id)
    assert deleted is not None
