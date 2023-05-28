from pydantic import BaseModel, EmailStr
from datetime import datetime, date
from typing import Optional


class UserOut(BaseModel):
    id: int
    name: str
    phone: str
    email: EmailStr

    class Config:
        orm_mode = True


class UserCreate(BaseModel):
    name: str
    phone: str
    email: EmailStr
    password: str


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    id: Optional[str] = None


class Account(BaseModel):
    id: int


class AccountCreate(BaseModel):
    user_id: int
    broker_id: int
    cash_balance: int
    line_available: int
    credit_limit: int
    pin: int


class AccountOut(Account):
    broker_id: int
    cash_balance: int
    line_available: int
    credit_limit: int

    class Config:
        orm_mode = True


class StockCreate(BaseModel):
    symbol: str
    company_name: str
    stock_industry: str
    market_value: int
    volume: int
    address: str
    telephone: str
    website: str
    registered_capital: int
    established_date: date
    market_entry_date: date
    ipo_price: float
    free_float: int
    major_shareholders: int

    class Config:
        orm_mode = True


class StockOut(BaseModel):
    symbol: str
    company_name: str

    class Config:
        orm_mode = True


class StockOutMarket(BaseModel):
    symbol: str
    close: float
    open: float
    change: float
    value: float

    class Config:
        orm_mode = True


class BrokerOut(BaseModel):
    name: str

    class Config:
        orm_mode = True


class BrokerCreate(BaseModel):
    name: str
    api_key: str

    class Config:
        orm_mode = True


class BankTransactionCreate(BaseModel):
    account_id: int
    type: str
    amount: int

    class Config:
        orm_mode = True


class BankTransactionOut(BaseModel):
    id: int
    type: str
    amount: int
    timestamp: datetime

    class Config:
        orm_mode = True


class OrderCreate(BaseModel):
    account_id: int
    symbol: str
    type: str
    volume: int
    price: float
    side: str
    validity: str
    pin: int

    class Config:
        orm_mode = True


class OrderCancel(BaseModel):
    id: int
    pin: int

    class Config:
        orm_mode = True


class OrderOut(BaseModel):
    id: int
    account_id: int
    symbol: str
    type: str
    volume: int
    price: float
    side: str
    validity: str
    time: datetime
    status: str

    class Config:
        orm_mode = True


class StockSearch(BaseModel):
    symbol: str
    close: float
    change: float


class DividendCreate(BaseModel):
    symbol: str
    account_id: int
    value: int

    class Config:
        orm_mode = True


class DividendOut(DividendCreate):
    id: int
    timestamp: datetime

    class Config:
        orm_mode = True


class NotiOut(BaseModel):
    id: int
    message: str
    volume: int
    price: float
    created_at: datetime

    class Config:
        orm_mode = True


class PortfolioCreate(BaseModel):
    account_id: int
    symbol: str
    volume: int
    price: float

    class Config:
        orm_mode = True


class PortfolioOut(BaseModel):
    symbol: str
    volume: int
    avg_price: float
    last_price: float
    change: float
    open: float
    close: float
    high: float
    low: float
    market_status: str

    class Config:
        orm_mode = True


class LoginOut(BaseModel):
    login: datetime
    device: str
    ip: str

    class Config:
        orm_mode = True
