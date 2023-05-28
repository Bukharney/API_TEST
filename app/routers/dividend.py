from fastapi import Depends, status, HTTPException, APIRouter
from app import oauth2
from .. import models, schemas
from ..database import get_db
from sqlalchemy.orm import Session

router = APIRouter(prefix="/dividend", tags=["dividend"])


@router.get(
    "/",
    status_code=status.HTTP_200_OK,
)
def get_all_dividend(
    current_user: int = Depends(oauth2.get_current_user),
    db: Session = Depends(get_db),
):
    dividend = (
        db.query(models.Dividend).order_by(models.Dividend.timestamp.desc()).all()
    )

    return dividend


@router.post(
    "/",
    response_model=schemas.DividendOut,
    status_code=status.HTTP_201_CREATED,
)
def create_dividend(
    dividend: schemas.DividendCreate,
    current_user: int = Depends(oauth2.get_current_user),
    db: Session = Depends(get_db),
):
    if not current_user.role != "broker" and current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only brokers can create dividends",
        )

    broker_account = (
        db.query(models.Accounts)
        .filter(models.Accounts.user_id == current_user.id)
        .first()
    )

    client_account = (
        db.query(models.Accounts)
        .filter(models.Accounts.id == dividend.account_id)
        .first()
    )

    if not broker_account.broker_id == client_account.broker_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only create dividends for your own broker",
        )

    new_dividend = models.Dividend(**dividend.dict())
    db.add(new_dividend)
    db.commit()
    db.refresh(new_dividend)
    return new_dividend


@router.get(
    "/{symbol}",
    response_model=schemas.DividendOut,
)
def get_dividend(
    symbol: str,
    current_user: int = Depends(oauth2.get_current_user),
    db: Session = Depends(get_db),
):
    account = (
        db.query(models.Accounts)
        .filter(models.Accounts.user_id == current_user.id)
        .first()
    )

    if not account:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Account not found"
        )

    dividend = (
        db.query(models.Dividend)
        .filter(models.Dividend.symbol == symbol)
        .filter(models.Dividend.account_id == account.id)
        .first()
    )

    return dividend


@router.post(
    "/add",
    status_code=status.HTTP_201_CREATED,
)
def create_dividend(
    dividend: schemas.DividendCreate,
    current_user: int = Depends(oauth2.get_current_user),
    db: Session = Depends(get_db),
):
    new_dividend = models.Dividend(**dividend.dict())
    db.add(new_dividend)
    db.commit()
    db.refresh(new_dividend)
    return new_dividend
