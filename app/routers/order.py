from fastapi import Depends, status, HTTPException, APIRouter
from app import oauth2
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
    new_order = models.Orders(**order.dict())
    new_order.matched = 0
    new_order.stock_balance = order.order_volume
    new_order.order_status = "Pending"
    db.add(new_order)
    db.commit()
    db.refresh(new_order)
    return new_order


@router.get(
    "/{id}",
    response_model=schemas.OrderOut,
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
