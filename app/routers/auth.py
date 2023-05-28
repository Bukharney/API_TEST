from datetime import timedelta
from fastapi import APIRouter, Depends, status, HTTPException, Response
from fastapi.security.oauth2 import OAuth2PasswordRequestForm
from sqlalchemy import text
from sqlalchemy.orm import Session
from random import randint

from .. import database, schemas, models, utils, oauth2

router = APIRouter(tags=["Authentication"])


@router.post("/login", response_model=schemas.Token)
def login(
    user_credentials: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(database.get_db),
):
    user = (
        db.query(models.User)
        .filter(models.User.email == user_credentials.username)
        .first()
    )

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )

    if not utils.verify(user_credentials.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Invalid Credentials"
        )

    access_token = oauth2.create_access_token(data={"user_id": user.id})
    login = models.Login_Logout(
        id=randint(1, 1000000000),
        user_id=user.id,
        logout=utils.get_current_time()
        + timedelta(minutes=oauth2.ACCESS_TOKEN_EXPIRE_MINUTES),
        device="desktop",
        ip="0.0.0.0",
    )

    db.add(login)
    db.commit()
    db.refresh(login)

    return {"access_token": access_token, "token_type": "bearer"}


@router.post("/logout")
def logout(
    response: Response,
    db: Session = Depends(database.get_db),
    current_user: int = Depends(oauth2.get_current_user),
):
    user = db.query(models.User).filter(models.User.email == current_user.email).first()

    logout = (
        db.query(models.Login_Logout)
        .filter(models.Login_Logout.user_id == user.id)
        .order_by(models.Login_Logout.id.desc())
        .first()
    )

    if logout:
        if utils.get_current_time() < logout.logout:
            logout.logout = utils.get_current_time()
            db.add(logout)
            db.commit()
            db.refresh(logout)
            response.status_code = status.HTTP_200_OK
            return {"message": "User logged out successfully"}
    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="User already logged out",
    )


@router.get("/reset", status_code=status.HTTP_200_OK)
def get_news(
    db: Session = Depends(database.get_db),
    current_user: int = Depends(oauth2.get_current_user),
):
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admin can reset database",
        )
    sql = text(
        "DROP TABLE IF EXISTS login_logout, stocks, brokers, users, accounts, bank_tsc, orders, transactions, news, turnover, dividend, portfolio, alembic_version CASCADE;"
    )
    res = db.execute(sql)
    db.commit()
    return res
