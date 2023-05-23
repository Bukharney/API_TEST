import datetime
from passlib.context import CryptContext

from . import models

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str):
    return pwd_context.hash(password)


def verify(password: str, hashed_password: str):
    return pwd_context.verify(password, hashed_password)


def get_current_time():
    return datetime.datetime.utcnow().replace(tzinfo=datetime.timezone.utc)


def manage_order(db, order):
    return True


def transactions(db):
    buy_orders = (
        db.query(models.Orders)
        .filter(
            models.Orders.side == "Buy",
            models.Orders.status == "O",
        )
        .order_by(models.Orders.price.desc())
        .order_by(models.Orders.time.asc())
        .all()
    )

    sell_orders = (
        db.query(models.Orders)
        .filter(
            models.Orders.side == "Sell",
            models.Orders.status == "O",
        )
        .order_by(models.Orders.price.asc())
        .order_by(models.Orders.time.asc())
        .all()
    )

    for buy_order in buy_orders:
        for sell_order in sell_orders:
            if buy_order.symbol == sell_order.symbol:
                if buy_order.price >= sell_order.price:
                    if buy_order.balance >= sell_order.balance:
                        buy_transaction = models.Transactions(
                            order_id=buy_order.id,
                            transaction_price=sell_order.price,
                            transaction_volume=sell_order.balance,
                        )
                        sell_transaction = models.Transactions(
                            order_id=sell_order.id,
                            transaction_price=sell_order.price,
                            transaction_volume=sell_order.balance,
                        )
                        db.add(buy_transaction)
                        db.add(sell_transaction)
                        buy_order.balance -= sell_order.balance
                        sell_order.balance = 0
                        sell_order.status = "C"
                        sell_order.matched = sell_order.volume
                        buy_order.matched = buy_order.volume - buy_order.balance

                    else:
                        buy_transaction = models.Transactions(
                            order_id=buy_order.id,
                            transaction_price=sell_order.price,
                            transaction_volume=buy_order.balance,
                        )
                        sell_transaction = models.Transactions(
                            order_id=sell_order.id,
                            transaction_price=sell_order.price,
                            transaction_volume=buy_order.balance,
                        )

                        db.add(buy_transaction)
                        db.add(sell_transaction)
                        sell_order.balance -= buy_order.balance
                        buy_order.balance = 0
                        buy_order.status = "C"
                        buy_order.matched = buy_order.volume
                        sell_order.matched = sell_order.volume - sell_order.balance

                    db.commit()
                    db.refresh(buy_order)
                    db.refresh(sell_order)

    return True
