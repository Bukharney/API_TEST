from typing import List
from fastapi import Depends, status, HTTPException, APIRouter
from sqlalchemy import func
from app import api, oauth2, utils
from .. import models, schemas
from ..database import get_db
from sqlalchemy.orm import Session

router = APIRouter(prefix="/portfolio", tags=["Portfolio"])


@router.get(
    "/{account_id}",
    status_code=status.HTTP_200_OK,
    response_model=List[schemas.PortfolioOut],
)
def get_portfolio(
    account_id: int,
    current_user: int = Depends(oauth2.get_current_user),
    db: Session = Depends(get_db),
):
    account = (
        db.query(models.Accounts)
        .filter(models.Accounts.id == account_id)
        .filter(models.Accounts.user_id == current_user.id)
        .first()
    )
    if not account:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Account not found"
        )
    result = utils.get_portfolio(db=db, account_id=account_id)
    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Portfolio not found"
        )

    for symbol in result:
        price_info = api.get_price_info(symbol["symbol"])
        symbol["last_price"] = price_info["last"]
        symbol["change"] = price_info["change"]

    return result


@router.post(
    "/",
    status_code=status.HTTP_201_CREATED,
)
def create_portfolio(
    portfolio: schemas.PortfolioCreate,
    current_user: int = Depends(oauth2.get_current_user),
    db: Session = Depends(get_db),
):
    if current_user.role == "user":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Only brokers and admins can create portfolios",
        )

    broker_account = (
        db.query(models.Accounts)
        .filter(models.Accounts.user_id == current_user.id)
        .first()
    )

    if not broker_account:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Account not found"
        )

    user_account = (
        db.query(models.Accounts)
        .filter(models.Accounts.id == portfolio.account_id)
        .first()
    )

    if current_user.role == "broker":
        if broker_account.broker_id != user_account.broker_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You can only create portfolios for your own broker",
            )

    portfolio_exists = (
        db.query(models.Portfolio)
        .filter(models.Portfolio.account_id == portfolio.account_id)
        .filter(models.Portfolio.symbol == portfolio.symbol)
        .filter(models.Portfolio.price == portfolio.price)
        .first()
    )

    if portfolio_exists:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Portfolio already exists",
        )

    new_portfolio = models.Portfolio(**portfolio.dict())
    db.add(new_portfolio)
    db.commit()
    db.refresh(new_portfolio)
    return {
        "status": "success",
    }
