from typing import List
from fastapi import Depends, status, HTTPException, APIRouter
from app import oauth2
from .. import models, schemas
from ..database import get_db
from sqlalchemy.orm import Session
from settrade_v2 import Investor

investor = Investor(
    app_id="x878HsmA5yuk5XXR",
    app_secret="Yp5VyFlBxTgmljVkAmxOUpJDfmq9iESD+RE469PjMU8=",
    broker_id="SANDBOX",
    app_code="SANDBOX",
    is_auto_queue=False,
)

market = investor.MarketData()

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


@router.get("/", response_model=List[schemas.StockOut])
def get_all_stocks(
    current_user: int = Depends(oauth2.get_current_user),
    db: Session = Depends(get_db),
):
    stocks = db.query(models.Stock).all()
    return stocks


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


@router.get("/search/{symbol}", response_model=schemas.StockSearch)
def get_stock_search(
    symbol: str,
    current_user: int = Depends(oauth2.get_current_user),
    db: Session = Depends(get_db),
):
    result = (
        db.query(models.Stock).filter(models.Stock.symbol.like(f"%{symbol}%")).all()
    )
    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Stock not found"
        )

    return {"result": result, "count": len(result)}


@router.get("/market/{symbol}/{interval}/{limit}")
def get_stock_market(
    symbol: str,
    interval: str,
    limit: int,
    current_user: int = Depends(oauth2.get_current_user),
    db: Session = Depends(get_db),
):
    res = market.get_quote_symbol("AOT")

    if not res:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Stock not found"
        )

    return res
