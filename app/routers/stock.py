from fastapi import Depends, status, HTTPException, APIRouter
from app import oauth2
from .. import models, schemas
from ..database import get_db
from sqlalchemy.orm import Session

router = APIRouter(prefix="/stock", tags=["Stock"])


@router.post("/", response_model=schemas.StockOut, status_code=status.HTTP_201_CREATED)
def create_stock(
    stock: schemas.StockCreate,
    current_user: int = Depends(oauth2.get_current_user),
    db: Session = Depends(get_db),
):
    verify_account = (
        db.query(models.Stock).filter(models.Stock.symbol == stock.symbol).first()
    )
    if verify_account:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Stock with given symbol already exists",
        )
    new_stock = models.Stock(**stock.dict())
    db.add(new_stock)
    db.commit()
    db.refresh(new_stock)
    return new_stock


@router.get("/{symbol}", response_model=schemas.StockCreate)
def get_stock(
    symbol: str,
    current_user: int = Depends(oauth2.get_current_user),
    db: Session = Depends(get_db),
):
    stock = db.query(models.Stock).filter(models.Stock.symbol == symbol).first()
    if not stock:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Stock not found"
        )

    return stock
