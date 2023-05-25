from fastapi import Depends, status, HTTPException, APIRouter
from app import oauth2
from .. import models, schemas
from ..database import get_db
from sqlalchemy.orm import Session
from typing import List


router = APIRouter(prefix="/bank_tsc", tags=["Bank Transaction"])


@router.post(
    "/",
    response_model=schemas.BankTransactionOut,
    status_code=status.HTTP_201_CREATED,
)
def create_bank_transaction(
    bank_transaction: schemas.BankTransactionCreate,
    current_user: int = Depends(oauth2.get_current_user),
    db: Session = Depends(get_db),
):
    if current_user.role != "broker":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Only brokers can create bank transactions",
        )
    new_bank_transaction = models.Bank_transactions(**bank_transaction.dict())
    account = (
        db.query(models.Accounts)
        .filter(models.Accounts.id == bank_transaction.account_id)
        .first()
    )

    if not account:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Account not found"
        )

    if bank_transaction.type == "deposit":
        account.cash_balance += bank_transaction.amount
        account.line_available += bank_transaction.amount
    elif bank_transaction.type == "withdraw":
        if account.cash_balance < bank_transaction.amount:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Not enough funds in account",
            )
        account.cash_balance -= bank_transaction.amount
        account.line_available -= bank_transaction.amount
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Bank transaction type must be deposit or withdraw",
        )

    db.add(new_bank_transaction)
    db.commit()
    db.refresh(new_bank_transaction)
    return new_bank_transaction


@router.get(
    "/my",
    response_model=List[schemas.BankTransactionOut],
)
def get_all_bank_transactions(
    current_user: int = Depends(oauth2.get_current_user),
    db: Session = Depends(get_db),
):
    account = (
        db.query(models.Accounts)
        .filter(current_user.id == models.Accounts.user_id)
        .first()
    )
    if not account:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User does not have account"
        )

    bank_transactions = (
        db.query(models.Bank_transactions)
        .filter(current_user.id == account.user_id)
        .all()
    )

    if not bank_transactions:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Bank Transactions not found"
        )
    return bank_transactions


@router.get(
    "/{id}",
    response_model=schemas.BankTransactionOut,
)
def get_bank_transaction(
    id: int,
    current_user: int = Depends(oauth2.get_current_user),
    db: Session = Depends(get_db),
):
    bank_transaction = (
        db.query(models.Bank_transactions)
        .filter(models.Bank_transactions.id == id)
        .first()
    )
    if not bank_transaction:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Bank Transaction not found"
        )

    return bank_transaction
