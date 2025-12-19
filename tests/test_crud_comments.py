# tests/test_crud_comments.py
from app import crud


def test_create_and_list_comments(db_session):
    user = crud.create_user(db_session, {"name": "c_user", "email": "c@example.com"})
    news = crud.create_news(db_session, {"title": "n", "text": "t", "author_id": user.id})

    comment = crud.create_comment(
        db_session,
        {"text": "nice", "author_id": user.id, "news_id": news.id},
    )
    assert comment.id is not None
    assert comment.author_id == user.id

    comments = crud.get_comments(db_session)
    assert len(comments) == 1
    assert comments[0].id == comment.id


def test_update_and_delete_comment(db_session):
    user = crud.create_user(db_session, {"name": "u2", "email": "u2@example.com"})
    news = crud.create_news(db_session, {"title": "n2", "text": "t2", "author_id": user.id})

    comment = crud.create_comment(
        db_session,
        {"text": "old", "author_id": user.id, "news_id": news.id},
    )

    updated = crud.update_comment(db_session, comment.id, {"text": "new"})
    assert updated.text == "new"

    crud.delete_comment(db_session, comment.id)
    assert crud.get_comments(db_session) == []
