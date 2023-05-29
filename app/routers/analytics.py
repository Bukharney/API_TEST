import datetime
from typing import List
from fastapi import Depends, status, HTTPException, APIRouter
from sqlalchemy import case, func, text
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
    start_time = datetime.datetime(2023, 5, 29, 13, 00)
    end_time = datetime.datetime(2023, 5, 29, 14, 5)

    sql = text(
        """
    SELECT
        symbol,
        SUM(volume) AS vol_sum,
        price,
        COUNT(CASE WHEN side = 'Buy' THEN 1 END) AS total_buy_order,
        COUNT(CASE WHEN side = 'Sell' THEN 1 END) AS total_sell_order
    FROM
        orders
    WHERE 
        time BETWEEN :start_time AND :end_time
    GROUP BY
        symbol,
        volume,
        price;
    """
    ).bindparams(start_time=start_time, end_time=end_time)

    result = db.execute(sql).fetchall()

    orders = [
        {
            "symbol": row.symbol,
            "vol_sum": row.vol_sum,
            "price": row.price,
            "total_buy_order": row.total_buy_order,
            "total_sell_order": row.total_buy_order,
        }
        for row in result
    ]
    return orders
