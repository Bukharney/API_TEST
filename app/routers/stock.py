from typing import List
from fastapi import Depends, status, HTTPException, APIRouter
from app import oauth2, api, utils
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
    get_quote = utils.get_quote(db)
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
    symbol = symbol.upper()
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
    res = api.get_candlestick(symbol, interval, limit)

    if not res:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Stock not found"
        )

    return res


@router.get("/price_info/{symbol}")
def get_stock_market_price_info(
    symbol: str,
    current_user: int = Depends(oauth2.get_current_user),
):
    res = api.get_price_info(symbol)

    if not res:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Something went wrong"
        )

    return res


@router.get("/bid_offer/{symbol}")
def get_stock_market_bid_offer(
    symbol: str,
    current_user: int = Depends(oauth2.get_current_user),
):
    res = api.get_bid_offer(symbol)

    if not res:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Something went wrong"
        )

    return res


@router.get("/transactions/{account_id}")
def get_my_transactions(
    account_id: int,
    current_user: int = Depends(oauth2.get_current_user),
    db: Session = Depends(get_db),
):
    transactions = (
        db.query(models.Transactions)
        .join(
            models.Orders,
            onclause=models.Transactions.order_id == models.Orders.id,
        )
        .filter(models.Orders.account_id == account_id)
        .order_by(models.Transactions.timestamp.desc())
        .all()
    )

    for transaction in transactions:
        order = (
            db.query(models.Orders)
            .filter(models.Orders.id == transaction.order_id)
            .first()
        )
        transaction.symbol = order.symbol
        transaction.side = order.side

    return transactions


@router.get("/market_data/{symbol}")
def func1(
    symbol: str,
    current_user: int = Depends(oauth2.get_current_user),
    db: Session = Depends(get_db),
):
    return api.get_market_data(symbol)
