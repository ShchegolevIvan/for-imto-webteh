from fastapi import APIRouter, Depends, Request, HTTPException, status
from sqlalchemy.orm import Session
from datetime import datetime, timezone
from app.db import get_db
from app import models
from app.security import hash_password, verify_password, new_access_token, new_refresh_token, jwt_decode

router = APIRouter(prefix="/auth", tags=["auth"])

@router.post("/register")
def register(data: dict, db: Session = Depends(get_db)):

    if db.query(models.User).filter(models.User.email == data.get("email")).first():
        raise HTTPException(409, "Email already registered")
    user = models.User(
        name=data.get("name"),
        email=data.get("email"),
        password_hash=hash_password(data.get("password")),
    )
    db.add(user); db.commit(); db.refresh(user)
    access = new_access_token(user.id, user.is_admin, user.is_verified_author)
    refresh, jti, exp_dt = new_refresh_token(user.id)
    db.add(models.RefreshSession(user_id=user.id, token_id=jti, user_agent="password-register", expires_at=exp_dt))
    db.commit()
    return {"access_token": access, "refresh_token": refresh, "token_type": "bearer"}

@router.post("/login")
def login(request: Request, data: dict, db: Session = Depends(get_db)):

    user = db.query(models.User).filter(models.User.email == data.get("email")).first()
    if not user or not user.password_hash or not verify_password(data.get("password",""), user.password_hash):
        raise HTTPException(401, "Invalid credentials")
    access = new_access_token(user.id, user.is_admin, user.is_verified_author)
    refresh, jti, exp_dt = new_refresh_token(user.id)
    ua = request.headers.get("User-Agent", "")
    db.add(models.RefreshSession(user_id=user.id, token_id=jti, user_agent=ua, expires_at=exp_dt))
    db.commit()
    return {"access_token": access, "refresh_token": refresh, "token_type": "bearer"}

@router.post("/refresh")
def refresh(request: Request, data: dict, db: Session = Depends(get_db)):

    try:
        payload = jwt_decode(data.get("refresh_token",""))
    except Exception:
        raise HTTPException(401, "Invalid refresh token")
    if payload.get("type") != "refresh":
        raise HTTPException(401, "Invalid token type")
    jti = payload.get("jti"); user_id = int(payload.get("sub"))
    rs = db.query(models.RefreshSession).filter(
        models.RefreshSession.user_id==user_id,
        models.RefreshSession.token_id==jti,
        models.RefreshSession.revoked==False,
        models.RefreshSession.expires_at > datetime.now(timezone.utc)
    ).first()
    if not rs:
        raise HTTPException(401, "Refresh session not found")
    user = db.get(models.User, user_id)
    access = new_access_token(user.id, user.is_admin, user.is_verified_author)

    return {"access_token": access, "token_type": "bearer"}

@router.post("/logout")
def logout(data: dict, db: Session = Depends(get_db)):

    try:
        payload = jwt_decode(data.get("refresh_token",""))
    except Exception:
        raise HTTPException(401, "Invalid refresh token")
    jti = payload.get("jti"); user_id = int(payload.get("sub"))
    rs = db.query(models.RefreshSession).filter(
        models.RefreshSession.user_id==user_id,
        models.RefreshSession.token_id==jti,
        models.RefreshSession.revoked==False
    ).first()
    if not rs:
        raise HTTPException(404, "Session not found")
    rs.revoked = True
    db.commit()
    return {"detail": "logged out"}

@router.get("/sessions")
def my_sessions(request: Request, db: Session = Depends(get_db)):
    from app.deps import get_current_user
    user = get_current_user(request, db)
    sessions = db.query(models.RefreshSession).filter(
        models.RefreshSession.user_id == user.id,
        models.RefreshSession.revoked == False,
    ).all()
    return [
        {
            "token_id": s.token_id,
            "user_agent": s.user_agent,
            "created_at": s.created_at,
            "expires_at": s.expires_at,
        } for s in sessions
    ]