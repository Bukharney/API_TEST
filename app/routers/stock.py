from typing import List
from fastapi import Depends, status, HTTPException, APIRouter
from app import oauth2, api, utils
from .. import models, schemas
from ..database import get_db
from sqlalchemy.orm import Session
from operator import itemgetter


router = APIRouter(prefix="/stock", tags=["Stock"])


@router.post("/", response_model=schemas.StockOut, status_code=status.HTTP_201_CREATED)
def create_stock(
    stock: schemas.StockCreate,
    current_user: int = Depends(oauth2.get_current_user),
    db: Session = Depends(get_db),
):
    if current_user.role != "admin" and current_user.role != "company":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="You are not authorized to create a stock",
        )

    stock.symbol = stock.symbol.upper()
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
    update_turnover = utils.get_quote(db)
    return new_stock


@router.get("/", response_model=List[schemas.StockOutMarket])
def get_all_stocks(
    current_user: int = Depends(oauth2.get_current_user),
    db: Session = Depends(get_db),
):
    stocks = db.query(models.Stock).limit(10).all()
    st = api.SetTradeSymbol().get_candlesticks(stocks, "1d", 1)
    sorted_stocks = sorted(stocks, key=lambda x: x.value, reverse=True)

    return sorted_stocks


@router.get("/company_info/all")
def stock_comp_info(
    current_user: int = Depends(oauth2.get_current_user),
    db: Session = Depends(get_db),
):
    info = db.query(models.Stock).all()
    return info


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


@router.get("/search/{symbol}", response_model=List[schemas.StockOutMarket])
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
        return []

    details = api.SetTradeSymbol().get_candlesticks(result, "1d", 1)

    return result


@router.get("/market/{symbol}/{interval}/{limit}")
def get_stock_market(
    symbol: str,
    interval: str,
    limit: int,
    current_user: int = Depends(oauth2.get_current_user),
    db: Session = Depends(get_db),
):
    res = api.SetTradeSymbol().get_candlestick(symbol, interval, limit)

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
    res = api.SetTradeSymbol().get_price_info(symbol)

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
    res = api.SetTradeSymbol().get_bid_offer(symbol)

    if not res:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Something went wrong"
        )

    return res


@router.get("/transactions/all")
def get_all_transactions(
    current_user: int = Depends(oauth2.get_current_user),
    db: Session = Depends(get_db),
):
    transaction = db.query(models.Transactions).all()

    return transaction


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
    return api.SetTradeSymbol().get_market_data(symbol)


@router.put("/update/{symbol}")
def update_stock(
    symbol: str,
    update_stock: schemas.StockCreate,
    current_user: int = Depends(oauth2.get_current_user),
    db: Session = Depends(get_db),
):
    if current_user.role != "admin" and current_user.role != "company":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="You are not authorized to update a stock",
        )

    symbol = symbol.upper()
    stock = db.query(models.Stock).filter(models.Stock.symbol == symbol).first()
    if not stock:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Stock not found"
        )

    stock.symbol = update_stock.symbol.upper()
    stock.address = update_stock.address
    stock.company_name = update_stock.company_name
    stock.stock_industry = update_stock.stock_industry
    stock.market_value = update_stock.market_value
    stock.volume = update_stock.volume
    stock.address = update_stock.address
    stock.website = update_stock.website
    stock.registered_capital = update_stock.registered_capital
    stock.established_date = update_stock.established_date
    stock.market_entry_date = update_stock.market_entry_date
    stock.ipo_price = update_stock.ipo_price
    stock.free_float = update_stock.free_float
    stock.major_shareholders = update_stock.major_shareholders
    db.commit()
    db.refresh(stock)

    return stock


@router.delete("/delete/{symbol}")
def delete_stock(
    symbol: str,
    current_user: int = Depends(oauth2.get_current_user),
    db: Session = Depends(get_db),
):
    if current_user.role != "admin" and current_user.role != "company":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="You are not authorized to delete a stock",
        )

    symbol = symbol.upper()
    stock = db.query(models.Stock).filter(models.Stock.symbol == symbol).first()
    if not stock:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Stock not found"
        )

    db.delete(stock)
    db.commit()

    return {"message": "Stock deleted successfully"}


@router.post("/transactions")
def create_transaction(
    transaction: schemas.TransactionCreate,
    current_user: int = Depends(oauth2.get_current_user),
    db: Session = Depends(get_db),
):
    if current_user.role != "admin" and current_user.role != "broker":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="You are not authorized to create a transaction",
        )

    order = db.query(models.Orders).filter(models.Orders.id == transaction.order_id)
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Order not found"
        )

    new_transaction = models.Transactions(
        order_id=transaction.order_id,
        price=transaction.price,
        volume=transaction.volume,
    )
    db.add(new_transaction)
    db.commit()
    db.refresh(new_transaction)

    return transaction
