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
    broker = (
        db.query(models.Broker).filter(models.Broker.id == account.broker_id).first()
    )
    if not broker:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Given broker not found"
        )

    new_account = models.Accounts(**account.dict(), user_id=current_user.id)
    try:
        db.add(new_account)
        db.commit()
        db.refresh(new_account)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))

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
    broker = (
        db.query(models.Broker).filter(models.Broker.id == account.broker_id).first()
    )

    account.broker_name = broker.name
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


@router.get(
    "/verify_balance/{account_id}/{broker_id}",
    status_code=status.HTTP_200_OK,
)
def get_portfolio(
    account_id: int,
    broker_id: int,
    current_user: int = Depends(oauth2.get_current_user),
    db: Session = Depends(get_db),
):
    if current_user.role == "user":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="You are not authorized to perform this action",
        )

    account = db.query(models.Accounts).filter(models.Accounts.id == account_id).first()
    broker_account = (
        db.query(models.Accounts)
        .filter(models.Accounts.user_id == current_user.id)
        .first()
    )
    if not account:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Account not found"
        )

    if not broker_account.broker_id == account.broker_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="You are not authorized to perform this action",
        )

    account.cash_balance = account.line_available
    db.commit()
    db.refresh(account)

    return {
        "result": "success",
    }
