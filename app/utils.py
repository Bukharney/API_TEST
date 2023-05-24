import datetime
from passlib.context import CryptContext
from sqlalchemy import func

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
            if buy_order.account_id != sell_order.account_id:
                account = (
                    db.query(models.Accounts)
                    .filter(models.Accounts.id == sell_order.account_id)
                    .first()
                )
                if buy_order.symbol == sell_order.symbol:
                    if buy_order.price >= sell_order.price:
                        buyyer_portfolio = (
                            db.query(models.Portfolio)
                            .filter(
                                models.Portfolio.account_id == buy_order.account_id,
                                models.Portfolio.symbol == buy_order.symbol,
                                models.Portfolio.price == buy_order.price,
                            )
                            .first()
                        )
                        seller_portfolio = (
                            db.query(models.Portfolio)
                            .filter(
                                models.Portfolio.account_id == sell_order.account_id,
                                models.Portfolio.symbol == sell_order.symbol,
                                models.Portfolio.price == sell_order.price,
                            )
                            .first()
                        )
                        if buy_order.balance > sell_order.balance:
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

                            if not buyyer_portfolio:
                                buyyer_portfolio = models.Portfolio(
                                    account_id=buy_order.account_id,
                                    symbol=buy_order.symbol,
                                    volume=0,
                                    price=sell_order.price,
                                )
                                db.add(buyyer_portfolio)
                            if not seller_portfolio:
                                seller_portfolio = models.Portfolio(
                                    account_id=sell_order.account_id,
                                    symbol=sell_order.symbol,
                                    volume=0,
                                    price=sell_order.price,
                                )
                                db.add(seller_portfolio)

                            buyyer_portfolio.volume += sell_order.balance
                            seller_portfolio.volume -= sell_order.balance
                            db.add(buyyer_portfolio)
                            db.add(seller_portfolio)

                            db.add(buy_transaction)
                            db.add(sell_transaction)

                            account.line_available += (
                                sell_order.balance * sell_order.price
                            )

                            buy_order.balance -= sell_order.balance
                            sell_order.balance = 0
                            sell_order.status = "C"
                            sell_order.matched = sell_order.volume
                            buy_order.matched = buy_order.volume - buy_order.balance

                        elif buy_order.balance < sell_order.balance:
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

                            if not buyyer_portfolio:
                                buyyer_portfolio = models.Portfolio(
                                    account_id=buy_order.account_id,
                                    symbol=buy_order.symbol,
                                    volume=0,
                                    price=sell_order.price,
                                )
                                db.add(buyyer_portfolio)
                            if not seller_portfolio:
                                seller_portfolio = models.Portfolio(
                                    account_id=sell_order.account_id,
                                    symbol=sell_order.symbol,
                                    volume=0,
                                    price=sell_order.price,
                                )
                                db.add(seller_portfolio)

                            buyyer_portfolio.volume += buy_order.balance
                            seller_portfolio.volume -= buy_order.balance
                            db.add(buyyer_portfolio)
                            db.add(seller_portfolio)

                            db.add(buy_transaction)
                            db.add(sell_transaction)

                            account.line_available += (
                                buy_order.balance
                            ) * sell_order.price

                            sell_order.balance -= buy_order.balance
                            buy_order.balance = 0
                            buy_order.status = "C"
                            buy_order.matched = buy_order.volume
                            sell_order.matched = sell_order.volume - sell_order.balance

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

                            if not buyyer_portfolio:
                                buyyer_portfolio = models.Portfolio(
                                    account_id=buy_order.account_id,
                                    symbol=buy_order.symbol,
                                    volume=0,
                                    price=sell_order.price,
                                )
                                db.add(buyyer_portfolio)
                            if not seller_portfolio:
                                seller_portfolio = models.Portfolio(
                                    account_id=sell_order.account_id,
                                    symbol=sell_order.symbol,
                                    volume=0,
                                    price=sell_order.price,
                                )
                                db.add(seller_portfolio)

                            buyyer_portfolio.volume += sell_order.balance
                            seller_portfolio.volume -= sell_order.balance
                            db.add(buyyer_portfolio)
                            db.add(seller_portfolio)

                            db.add(buy_transaction)
                            db.add(sell_transaction)

                            account.line_available += (
                                sell_order.balance * sell_order.price
                            )
                            sell_order.balance = 0
                            buy_order.balance = 0
                            buy_order.status = "C"
                            sell_order.status = "C"
                            buy_order.matched = buy_order.volume
                            sell_order.matched = sell_order.volume

                        db.commit()
                        db.refresh(buy_order)
                        db.refresh(sell_order)
                        db.refresh(buyyer_portfolio)
                        db.refresh(seller_portfolio)

    return True


def get_portfolio(db, account_id):
    port = (
        db.query(models.Portfolio)
        .filter(models.Portfolio.account_id == account_id)
        .all()
    )

    symbol_volume = {}
    symbol_total_price = {}

    for item in port:
        volume = item.volume
        symbol = item.symbol
        price = item.price

        if symbol not in symbol_volume:
            symbol_volume[symbol] = 0
            symbol_total_price[symbol] = 0

        symbol_volume[symbol] += volume
        symbol_total_price[symbol] += volume * price

    result = []
    print("Net Volume and Average Price for Each Symbol:")
    for symbol in symbol_volume:
        volume = symbol_volume[symbol]
        total_price = symbol_total_price[symbol]
        avg_price = total_price / abs(volume)
        print(symbol, "Net Volume:", volume, "Average Price:", avg_price)
        result.append(
            {
                "symbol": symbol,
                "volume": volume,
                "average_price": round(avg_price, 2),
            }
        )
    if len(result) == 0:
        return {
            "message": "No portfolio for this account",
        }
    return result
