from fastapi import Depends, status, HTTPException, APIRouter
from app import oauth2
from .. import models, schemas
from ..database import get_db
from sqlalchemy.orm import Session

router = APIRouter(prefix="/dividend", tags=["dividend"])


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
