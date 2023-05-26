from typing import List
from fastapi import Depends, status, HTTPException, APIRouter

from app import oauth2

from .. import models, schemas, utils
from ..database import get_db
from sqlalchemy.orm import Session

router = APIRouter(prefix="/users", tags=["Users"])


@router.post("/", status_code=status.HTTP_201_CREATED, response_model=schemas.UserOut)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    hash_password = utils.hash_password(user.password)
    user.password = hash_password
    new_user = models.User(**user.dict())
    if db.query(models.User).filter(models.User.email == new_user.email).first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User with given email already exists",
        )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user


@router.get("/", response_model=List[schemas.UserOut])
def get_user(
    db: Session = Depends(get_db),
    current_user: int = Depends(oauth2.get_current_user),
):
    user = db.query(models.User).all()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User with given id not found"
        )
    return user


@router.get("/token", response_model=schemas.UserOut)
def get_user(
    current_user: int = Depends(oauth2.get_current_user),
):
    return current_user


@router.get("/login_info", response_model=list[schemas.LoginOut])
def update_user_login_info(
    db: Session = Depends(get_db),
    current_user: int = Depends(oauth2.get_current_user),
):
    user = db.query(models.User).filter(models.User.id == current_user.id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User with given id not found"
        )
    login = (
        db.query(models.Login_Logout)
        .filter(models.Login_Logout.user_id == current_user.id)
        .order_by(models.Login_Logout.id.desc())
        .all()
    )

    if not login:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Something went wrong, please try again",
        )
    return login


@router.get("/{id}", response_model=schemas.UserOut)
def get_user(
    id: int,
    db: Session = Depends(get_db),
    current_user: int = Depends(oauth2.get_current_user),
):
    user = db.query(models.User).filter(models.User.id == id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User with given id not found"
        )
    return user
