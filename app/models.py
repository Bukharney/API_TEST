from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, Float, BigInteger
from sqlalchemy.orm import relationship
from sqlalchemy.sql.expression import text
from sqlalchemy.sql.sqltypes import TIMESTAMP

from .database import Base


class Post(Base):
    __tablename__ = "posts"

    id = Column(Integer, primary_key=True, nullable=False)
    title = Column(String, nullable=False)
    content = Column(String, nullable=False)
    published = Column(Boolean, server_default="TRUE", nullable=False)
    created_at = Column(
        TIMESTAMP(timezone=True), nullable=False, server_default=text("now()")
    )
    owner_id = Column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )

    owner = relationship("User")


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, nullable=False)
    email = Column(String, nullable=False, unique=True)
    password = Column(String, nullable=False)
    created_at = Column(
        TIMESTAMP(timezone=True), nullable=False, server_default=text("now()")
    )


class Broker(Base):
    __tablename__ = "brokers"
    id = Column(Integer, primary_key=True, nullable=False)
    name = Column(String, nullable=False)
    api_key = Column(String, nullable=False)
    created_at = Column(
        TIMESTAMP(timezone=True), nullable=False, server_default=text("now()")
    )


class Stock(Base):
    __tablename__ = "stocks"
    symbol = Column(String, primary_key=True, nullable=False)
    company_name = Column(String, nullable=False)
    stock_industry = Column(String, nullable=False)
    market_value = Column(BigInteger, nullable=False)
    volume = Column(BigInteger, nullable=False)
    address = Column(String, nullable=False)
    telephone = Column(String, nullable=False)
    website = Column(String, nullable=False)
    registered_capital = Column(BigInteger, nullable=False)
    established_date = Column(TIMESTAMP(timezone=True), nullable=False)
    market_entry_date = Column(TIMESTAMP(timezone=True), nullable=False)
    ipo_price = Column(Float, nullable=False)
    free_float = Column(Integer, nullable=False)
    major_shareholders = Column(Integer, nullable=False)
    created_at = Column(
        TIMESTAMP(timezone=True), nullable=False, server_default=text("now()")
    )


class Login_Logout(Base):
    __tablename__ = "login_logout"
    id = Column(Integer, primary_key=True, nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"))
    login = Column(
        TIMESTAMP(timezone=True), nullable=False, server_default=text("now()")
    )
    logout = Column(TIMESTAMP(timezone=True))
    device = Column(String)


class Accounts(Base):
    __tablename__ = "accounts"
    id = Column(Integer, primary_key=True, nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"))
    broker_id = Column(Integer, ForeignKey("brokers.id"))
    cash_balance = Column(Integer, nullable=False)
    line_available = Column(Integer, nullable=False)
    credit_limit = Column(Integer, nullable=False)
    pin = Column(Integer, nullable=False)
    created_at = Column(
        TIMESTAMP(timezone=True), nullable=False, server_default=text("now()")
    )


class Bank_transactions(Base):
    __tablename__ = "bank_tsc"
    id = Column(Integer, primary_key=True, nullable=False)
    account_id = Column(Integer, ForeignKey("accounts.id"))
    transaction_type = Column(String, nullable=False)
    transaction_status = Column(String, nullable=False)
    transaction_amount = Column(Integer, nullable=False)
    transaction_time = Column(
        TIMESTAMP(timezone=True), nullable=False, server_default=text("now()")
    )


class Orders(Base):
    __tablename__ = "orders"
    id = Column(Integer, primary_key=True, nullable=False)
    account_id = Column(Integer, ForeignKey("accounts.id"))
    symbol = Column(String, ForeignKey("stocks.symbol"))
    stock_balance = Column(Integer, nullable=False)
    order_type = Column(String, nullable=False)
    order_status = Column(String, nullable=False)
    order_price = Column(Integer, nullable=False)
    order_volume = Column(Integer, nullable=False)
    order_side = Column(String, nullable=False)
    matched = Column(Integer, nullable=False)
    cancelled = Column(Integer, nullable=False)
    validity = Column(String, nullable=False)
    order_time = Column(
        TIMESTAMP(timezone=True), nullable=False, server_default=text("now()")
    )


class Transactions(Base):
    __tablename__ = "transactions"
    id = Column(Integer, primary_key=True, nullable=False)
    order_id = Column(Integer, ForeignKey("orders.id"))
    transaction_price = Column(Integer, nullable=False)
    transaction_volume = Column(Integer, nullable=False)
    transaction_time = Column(
        TIMESTAMP(timezone=True), nullable=False, server_default=text("now()")
    )


class Turnover(Base):
    __tablename__ = "turnover"
    id = Column(Integer, primary_key=True, nullable=False)
    symbol = Column(String, ForeignKey("stocks.symbol"))
    asset = Column(Integer, nullable=False)
    dept = Column(Integer, nullable=False)
    p_bv = Column(Integer, nullable=False)
    eps = Column(Integer, nullable=False)
    dividend_per_unit = Column(Integer, nullable=False)
    net_profit = Column(Integer, nullable=False)
    turnover_time = Column(
        TIMESTAMP(timezone=True), nullable=False, server_default=text("now()")
    )


class Dividend(Base):
    __tablename__ = "dividend"
    id = Column(Integer, primary_key=True, nullable=False)
    symbol = Column(String, ForeignKey("stocks.symbol"))
    account_id = Column(Integer, ForeignKey("accounts.id"))
    value = Column(Integer, nullable=False)
    transaction_time = Column(
        TIMESTAMP(timezone=True), nullable=False, server_default=text("now()")
    )


class News(Base):
    __tablename__ = "news"
    id = Column(Integer, primary_key=True, nullable=False)
    file = Column(String, nullable=False)
    topic = Column(String, nullable=False)
    content = Column(String, nullable=False)
    news_time = Column(TIMESTAMP(timezone=True), nullable=False)
