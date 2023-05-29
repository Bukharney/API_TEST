from typing import List
from fastapi import Depends, status, HTTPException, APIRouter
from sqlalchemy import func
from app import oauth2, utils
from .. import models, schemas
from ..database import get_db
from sqlalchemy.orm import Session

router = APIRouter(prefix="/analytics", tags=["Analytics"])


@router.get("/most_vol_stock")
def get_all_accounts(
    current_user: int = Depends(oauth2.get_current_user),
    db: Session = Depends(get_db),
):
    accounts = db.query(
        models.Orders.symbol,
        models.Orders.volume,
        models.Orders.price,
        func.count(func.case([(models.Orders.side == "Buy", 1)], else_=None)).label(
            "buy_count"
        ),
        func.count(func.case([(models.Orders.side == "Sell", 1)], else_=None)).label(
            "sell_count"
        ),
    ).group_by(models.Orders.symbol, models.Orders.volume, models.Orders.price)

    result = accounts.all()
    return accounts
