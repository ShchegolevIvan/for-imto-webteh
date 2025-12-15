import os
from fastapi import APIRouter, Depends, Request, HTTPException
from sqlalchemy.orm import Session
from fastapi_sso.sso.github import GithubSSO
from app.db import get_db
from app import models
from app.security import new_access_token, new_refresh_token

router = APIRouter(prefix="/auth/github", tags=["auth"])

sso = GithubSSO(
    client_id=os.getenv("GITHUB_CLIENT_ID",""),
    client_secret=os.getenv("GITHUB_CLIENT_SECRET",""),
    redirect_uri=os.getenv("GITHUB_REDIRECT_URL","http://localhost:8000/auth/github/callback"),
    allow_insecure_http=True,
)

@router.get("/login")
async def github_login():
    return await sso.get_login_redirect()

@router.get("/callback")
async def github_callback(request: Request, db: Session = Depends(get_db)):
    user = await sso.verify_and_process(request)

    gh_id = str(user.id)
    account = db.query(models.User).filter(models.User.github_id == gh_id).first()
    if not account:

        account = db.query(models.User).filter(models.User.email == (user.email or "")).first()
        if account:
            account.github_id = gh_id
            account.github_login = user.display_name
        else:
            account = models.User(
                name=user.display_name or "GitHub User",
                email=user.email or f"gh_{gh_id}@users.noreply.github.com",
                github_id=gh_id,
                github_login=user.display_name,
            )
            db.add(account)
        db.commit(); db.refresh(account)
    access = new_access_token(account.id, account.is_admin, account.is_verified_author)
    refresh, jti, exp_dt = new_refresh_token(account.id)
    ua = request.headers.get("User-Agent","")
    db.add(models.RefreshSession(user_id=account.id, token_id=jti, user_agent=ua, expires_at=exp_dt))
    db.commit()

    return {"access_token": access, "refresh_token": refresh, "token_type": "bearer"}