from typing import List
from fastapi import Depends, status, HTTPException, APIRouter
from app import oauth2, utils
from .. import models, schemas
from ..database import get_db
from sqlalchemy.orm import Session

router = APIRouter(prefix="/order", tags=["Order"])


@router.post(
    "/",
    response_model=schemas.OrderOut,
    status_code=status.HTTP_201_CREATED,
)
def create_order(
    order: schemas.OrderCreate,
    current_user: int = Depends(oauth2.get_current_user),
    db: Session = Depends(get_db),
):
    account = (
        db.query(models.Accounts).filter(models.Accounts.id == order.account_id).first()
    )
    if not account:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Account not found"
        )

    symbol = db.query(models.Stock).filter(models.Stock.symbol == order.symbol).first()
    if not symbol:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Symbol not found"
        )

    hash_password_pin = utils.hash_password(str(order.pin))
    verify_pin = utils.verify(str(order.pin), account.pin)
    if not verify_pin:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials"
        )
    del order.pin
    new_order = models.Orders(**order.dict())
    new_order.matched = 0
    new_order.balance = order.volume
    new_order.status = "O"
    new_order.cancelled = 0

    cost = order.volume * order.price

    port = utils.get_portfolio(db=db, account_id=order.account_id)

    if order.side == "Buy":
        if account.line_available < cost:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Insufficient balance"
            )
        account.line_available -= cost
    elif order.side == "Sell":
        if not port:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="No stocks to sell"
            )
        for item in port:
            volume = item["volume"]
            symbol = item["symbol"]
            if symbol == order.symbol:
                if volume < order.volume:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="You don't have enough stocks to sell",
                    )

    db.add(new_order)
    db.commit()
    db.refresh(new_order)

    utils.transactions(
        db=db,
    )

    return new_order


@router.get(
    "/all",
    status_code=status.HTTP_200_OK,
)
def get_orders(
    current_user: int = Depends(oauth2.get_current_user),
    db: Session = Depends(get_db),
):
    orders = db.query(models.Orders).all()
    if not orders:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Order not found"
        )

    return orders


@router.get(
    "/{account_id}",
    response_model=List[schemas.OrderOut],
    status_code=status.HTTP_200_OK,
)
def get_orders(
    account_id: int,
    current_user: int = Depends(oauth2.get_current_user),
    db: Session = Depends(get_db),
):
    orders = (
        db.query(models.Orders)
        .filter(models.Orders.account_id == account_id)
        .order_by(models.Orders.time.desc())
        .all()
    )
    if not orders:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Order not found"
        )

    return orders


@router.get(
    "/one/{id}",
    response_model=schemas.OrderOut,
    status_code=status.HTTP_200_OK,
)
def get_order(
    id: int,
    current_user: int = Depends(oauth2.get_current_user),
    db: Session = Depends(get_db),
):
    order = db.query(models.Orders).filter(models.Orders.id == id).first()
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Order not found"
        )

    return order


@router.get(
    "/cancel/{id}",
    status_code=status.HTTP_200_OK,
)
def get_orders(
    id: int,
    current_user: int = Depends(oauth2.get_current_user),
    db: Session = Depends(get_db),
):
    order = db.query(models.Orders).filter(models.Orders.id == id).first()
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Order not found"
        )
    account = (
        db.query(models.Accounts).filter(models.Accounts.id == order.account_id).first()
    )
    if account.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="You are not authorized to cancal this order",
        )

    order.cancelled = 1
    order.status = "C"
    account = (
        db.query(models.Accounts).filter(models.Accounts.id == order.account_id).first()
    )
    account.line_available += order.balance * order.price

    db.commit()
    db.refresh(order)
    return {
        "result": "Order cancelled successfully",
    }


@router.get(
    "/endofday",
    status_code=status.HTTP_200_OK,
)
def get_orders(
    current_user: int = Depends(oauth2.get_current_user),
    db: Session = Depends(get_db),
):
    orders = db.query(models.Orders).filter(models.Orders.status == "O").all()
    for order in orders:
        order.cancelled = 1
        order.status = "C"
        account = (
            db.query(models.Accounts)
            .filter(models.Accounts.id == order.account_id)
            .first()
        )
        account.line_available += order.balance * order.price

    db.commit()
    return {
        "result": "End of day",
    }
