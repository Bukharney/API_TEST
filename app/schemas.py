from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional

from pydantic.types import conint


class PostBase(BaseModel):
    title: str
    content: str
    published: bool = True


class PostCreate(PostBase):
    pass


class UserOut(BaseModel):
    id: int
    email: EmailStr
    created_at: datetime

    class Config:
        orm_mode = True


class Post(PostBase):
    id: int
    created_at: datetime
    owner_id: int
    owner: UserOut

    class Config:
        orm_mode = True


class PostOut(BaseModel):
    Post: Post
    votes: int

    class Config:
        orm_mode = True


class UserCreate(BaseModel):
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


class Vote(BaseModel):
    post_id: int
    dir: conint(le=1)


class Account(BaseModel):
    id: int


class AccountCreate(BaseModel):
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
    established_date: datetime
    market_entry_date: datetime
    ipo_price: int
    free_float: int
    major_shareholders: int

    class Config:
        orm_mode = True


class StockOut(BaseModel):
    symbol: str

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
    transaction_type: str
    transaction_status: str
    transaction_amount: int

    class Config:
        orm_mode = True


class BankTransactionOut(BankTransactionCreate):
    id: int
    transaction_time: datetime

    class Config:
        orm_mode = True
