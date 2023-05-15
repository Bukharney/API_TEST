from typing import List
from fastapi import Depends, status, HTTPException, APIRouter
from app import oauth2
from .. import models, schemas
from ..database import get_db
from sqlalchemy.orm import Session


router = APIRouter(prefix="/account", tags=["Account"])


@router.post(
    "/", response_model=schemas.AccountOut, status_code=status.HTTP_201_CREATED
)
def create_account(
    account: schemas.AccountCreate,
    current_user: int = Depends(oauth2.get_current_user),
    db: Session = Depends(get_db),
):
    new_account = models.Accounts(**account.dict(), user_id=current_user.id)
    db.add(new_account)
    db.commit()
    db.refresh(new_account)
    return new_account


@router.get("/{id}", response_model=schemas.AccountOut)
def get_account(
    id: int,
    current_user: int = Depends(oauth2.get_current_user),
    db: Session = Depends(get_db),
):
    account = (
        db.query(models.Accounts)
        .filter(models.Accounts.id == id)
        .filter(current_user.id == models.Accounts.user_id)
        .first()
    )
    if not account:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Account not found"
        )

    return account


@router.get("/", response_model=List[schemas.AccountOut])
def get_all_accounts(
    current_user: int = Depends(oauth2.get_current_user),
    db: Session = Depends(get_db),
):
    accounts = (
        db.query(models.Accounts)
        .filter(current_user.id == models.Accounts.user_id)
        .all()
    )
    return accounts
