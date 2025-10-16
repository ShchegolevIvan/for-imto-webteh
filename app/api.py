from fastapi import APIRouter, Depends, Request, HTTPException, status
from sqlalchemy.orm import Session
from app.db import get_db
from app import crud, models
from app.deps import get_current_user, require_verified_author, require_owner_news, require_owner_comment

router = APIRouter()

@router.post("/users", status_code=status.HTTP_201_CREATED)
async def add_user(request: Request, db: Session = Depends(get_db), _=Depends(get_current_user)):
    data = await request.json()
    return crud.create_user(db, data).__dict__

@router.get("/users")
def list_users(db: Session = Depends(get_db), _=Depends(get_current_user)):
    return [u.__dict__ for u in crud.get_users(db)]


@router.post("/news", status_code=status.HTTP_201_CREATED)
async def add_news(request: Request, db: Session = Depends(get_db), user: models.User = Depends(require_verified_author)):
    data = await request.json()

    author = db.query(models.User).filter(models.User.id == data.get("author_id")).first()
    if not author:
        raise HTTPException(status_code=404, detail="Автор не найден")

    if not author.is_verified_author:
        raise HTTPException(status_code=403, detail="Пользователь не верифицирован как автор")
    return crud.create_news(db, data).__dict__

@router.get("/news")
def list_news(db: Session = Depends(get_db), _=Depends(get_current_user)):
    return [n.__dict__ for n in crud.get_news(db)]

@router.put("/news/{news_id}")
async def edit_news(news_id: int, request: Request, db: Session = Depends(get_db)):
    data = await request.json()
    news = crud.update_news(db, news_id, data)
    if not news:
        raise HTTPException(status_code=404, detail="Новость не найдена")
    return news.__dict__

@router.delete("/news/{news_id}")
def remove_news(news_id: int, db: Session = Depends(get_db)):
    news = crud.delete_news(db, news_id)
    if not news:
        raise HTTPException(status_code=404, detail="Новость не найдена")
    return {"detail": "Новость удалена"}

@router.post("/comments", status_code=status.HTTP_201_CREATED)
async def add_comment(request: Request, db: Session = Depends(get_db), user: models.User = Depends(get_current_user)):
    data = await request.json()
    data["author_id"] = user.id
    return crud.create_comment(db, data).__dict__

@router.get("/comments")
def list_comments(db: Session = Depends(get_db), _=Depends(get_current_user)):
    return [c.__dict__ for c in crud.get_comments(db)]

@router.put("/comments/{comment_id}")
async def edit_comment(
    comment_id: int,
    request: Request,
    db: Session = Depends(get_db),
    _comment: models.Comment = Depends(require_owner_comment),
):
    data = await request.json()
    comment = crud.update_comment(db, comment_id, data)
    return comment.__dict__

@router.delete("/comments/{comment_id}")
def remove_comment(
    comment_id: int,
    db: Session = Depends(get_db),
    _comment: models.Comment = Depends(require_owner_comment),
):
    crud.delete_comment(db, comment_id)
    return {"detail": "Комментарий удалён"}
