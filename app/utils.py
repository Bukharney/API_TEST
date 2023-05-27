import datetime
from passlib.context import CryptContext
from app import api

from . import models

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str):
    return pwd_context.hash(password)


def verify(password: str, hashed_password: str):
    return pwd_context.verify(password, hashed_password)


def get_current_time():
    return datetime.datetime.utcnow().replace(tzinfo=datetime.timezone.utc)


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

    if buy_orders and sell_orders:
        for buy_order in buy_orders:
            for sell_order in sell_orders:
                if buy_order.status == "C" or sell_order.status == "C":
                    break
                if buy_order.account_id != sell_order.account_id:
                    account = (
                        db.query(models.Accounts)
                        .filter(models.Accounts.id == sell_order.account_id)
                        .first()
                    )
                    if buy_order.symbol == sell_order.symbol:
                        if buy_order.price >= sell_order.price:
                            buyer_portfolio = (
                                db.query(models.Portfolio)
                                .filter(
                                    models.Portfolio.account_id == buy_order.account_id,
                                    models.Portfolio.symbol == buy_order.symbol,
                                )
                                .order_by(models.Portfolio.created_at)
                                .first()
                            )
                            seller_portfolio = (
                                db.query(models.Portfolio)
                                .filter(
                                    models.Portfolio.account_id
                                    == sell_order.account_id,
                                    models.Portfolio.symbol == sell_order.symbol,
                                )
                                .order_by(models.Portfolio.created_at)
                                .first()
                            )
                            if buy_order.balance > sell_order.balance:
                                buy_transaction = models.Transactions(
                                    order_id=buy_order.id,
                                    price=sell_order.price,
                                    volume=sell_order.balance,
                                )
                                sell_transaction = models.Transactions(
                                    order_id=sell_order.id,
                                    price=sell_order.price,
                                    volume=sell_order.balance,
                                )
                                db.add(buy_transaction)
                                db.add(sell_transaction)

                                if not buyer_portfolio:
                                    buyer_portfolio = models.Portfolio(
                                        account_id=buy_order.account_id,
                                        symbol=buy_order.symbol,
                                        volume=0,
                                        price=sell_order.price,
                                    )
                                    db.add(buyer_portfolio)
                                if not seller_portfolio:
                                    seller_portfolio = models.Portfolio(
                                        account_id=sell_order.account_id,
                                        symbol=sell_order.symbol,
                                        volume=0,
                                        price=sell_order.price,
                                    )
                                    db.add(seller_portfolio)

                                buyer_portfolio.volume += sell_order.balance
                                seller_portfolio.volume -= sell_order.balance
                                db.add(buyer_portfolio)
                                db.add(seller_portfolio)

                                account.line_available += (
                                    sell_order.balance * sell_order.price
                                )

                                buyer_nolti = models.Notifications(
                                    account_id=buy_order.account_id,
                                    message=f"Your order BUY : {buy_order.symbol} was executed",
                                    price=sell_order.price,
                                    volume=sell_order.balance,
                                )
                                seller_nolti = models.Notifications(
                                    account_id=sell_order.account_id,
                                    message=f"Your order SELL : {sell_order.symbol} was executed and closed",
                                    price=sell_order.price,
                                    volume=sell_order.balance,
                                )
                                db.add(buyer_nolti)
                                db.add(seller_nolti)

                                buy_order.balance -= sell_order.balance
                                sell_order.balance = 0
                                sell_order.status = "C"
                                sell_order.matched = sell_order.volume
                                buy_order.matched = buy_order.volume - buy_order.balance
                            elif buy_order.balance < sell_order.balance:
                                buy_transaction = models.Transactions(
                                    order_id=buy_order.id,
                                    price=sell_order.price,
                                    volume=buy_order.balance,
                                )
                                sell_transaction = models.Transactions(
                                    order_id=sell_order.id,
                                    price=sell_order.price,
                                    volume=buy_order.balance,
                                )
                                db.add(buy_transaction)
                                db.add(sell_transaction)

                                if not buyer_portfolio:
                                    buyer_portfolio = models.Portfolio(
                                        account_id=buy_order.account_id,
                                        symbol=buy_order.symbol,
                                        volume=0,
                                        price=sell_order.price,
                                    )
                                    db.add(buyer_portfolio)
                                if not seller_portfolio:
                                    seller_portfolio = models.Portfolio(
                                        account_id=sell_order.account_id,
                                        symbol=sell_order.symbol,
                                        volume=0,
                                        price=sell_order.price,
                                    )
                                    db.add(seller_portfolio)

                                buyer_portfolio.volume += buy_order.balance
                                seller_portfolio.volume -= buy_order.balance
                                db.add(buyer_portfolio)
                                db.add(seller_portfolio)

                                account.line_available += (
                                    buy_order.balance
                                ) * sell_order.price

                                buyer_nolti = models.Notifications(
                                    account_id=buy_order.account_id,
                                    message=f"Your order BUY : {buy_order.symbol} was executed and closed",
                                    price=sell_order.price,
                                    volume=buy_order.balance,
                                )
                                seller_nolti = models.Notifications(
                                    account_id=sell_order.account_id,
                                    message=f"Your order SELL : {sell_order.symbol} was executed",
                                    price=sell_order.price,
                                    volume=buy_order.balance,
                                )
                                db.add(buyer_nolti)
                                db.add(seller_nolti)

                                sell_order.balance -= buy_order.balance
                                buy_order.balance = 0
                                buy_order.status = "C"
                                buy_order.matched = buy_order.volume
                                sell_order.matched = (
                                    sell_order.volume - sell_order.balance
                                )
                            elif buy_order.balance == sell_order.balance:
                                buy_transaction = models.Transactions(
                                    order_id=buy_order.id,
                                    price=sell_order.price,
                                    volume=buy_order.balance,
                                )
                                sell_transaction = models.Transactions(
                                    order_id=sell_order.id,
                                    price=sell_order.price,
                                    volume=buy_order.balance,
                                )
                                db.add(buy_transaction)
                                db.add(sell_transaction)

                                if not buyer_portfolio:
                                    buyer_portfolio = models.Portfolio(
                                        account_id=buy_order.account_id,
                                        symbol=buy_order.symbol,
                                        volume=0,
                                        price=sell_order.price,
                                    )
                                    db.add(buyer_portfolio)
                                if not seller_portfolio:
                                    seller_portfolio = models.Portfolio(
                                        account_id=sell_order.account_id,
                                        symbol=sell_order.symbol,
                                        volume=0,
                                        price=sell_order.price,
                                    )
                                    db.add(seller_portfolio)

                                buyer_portfolio.volume += sell_order.balance
                                seller_portfolio.volume -= sell_order.balance
                                db.add(buyer_portfolio)
                                db.add(seller_portfolio)

                                account.line_available += (
                                    sell_order.balance * sell_order.price
                                )

                                buyer_nolti = models.Notifications(
                                    account_id=buy_order.account_id,
                                    message=f"Your order BUY : {buy_order.symbol} was executed and closed",
                                    price=sell_order.price,
                                    volume=sell_order.balance,
                                )
                                seller_nolti = models.Notifications(
                                    account_id=sell_order.account_id,
                                    message=f"Your order SELL : {sell_order.symbol} was executed and closed",
                                    price=sell_order.price,
                                    volume=sell_order.balance,
                                )
                                db.add(buyer_nolti)
                                db.add(seller_nolti)

                                sell_order.balance = 0
                                buy_order.balance = 0
                                buy_order.status = "C"
                                sell_order.status = "C"
                                buy_order.matched = buy_order.volume
                                sell_order.matched = sell_order.volume

                            db.commit()
                            db.refresh(buy_order)
                            db.refresh(sell_order)
                            db.refresh(buyer_portfolio)
                            db.refresh(seller_portfolio)
                            db.refresh(account)
                            db.refresh(buyer_nolti)
                            db.refresh(seller_nolti)

    return True


def get_portfolio(db, account_id):
    port = (
        db.query(models.Portfolio)
        .filter(models.Portfolio.account_id == account_id)
        .all()
    )

    if not port:
        return False

    symbol_volume = {}
    symbol_total_price = {}
    value = 0

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
        if volume <= 0:
            avg_price = 0
        else:
            avg_price = total_price / abs(volume)
        print(symbol, "Net Volume:", volume, "Average Price:", avg_price)
        result.append(
            {
                "symbol": symbol,
                "volume": volume,
                "avg_price": round(avg_price, 2),
            }
        )
    return result


def get_quote(db):
    symbol = db.query(models.Stock).all()
    if not symbol:
        return False
    for i in symbol:
        res = api.get_quote_symbol(i.symbol)
        if not res:
            return False
        if (
            not db.query(models.Turnover)
            .filter(models.Turnover.symbol == i.symbol)
            .first()
        ):
            turnover = models.Turnover(
                symbol=i.symbol,
                pbv=res["pbv"],
                eps=res["eps"],
            )
            db.add(turnover)
            db.commit()
            db.refresh(turnover)
        else:
            update_turnover = (
                db.query(models.Turnover)
                .filter(models.Turnover.symbol == i.symbol)
                .first()
            )
            update_turnover.pbv = res["pbv"]
            update_turnover.eps = res["eps"]
            db.commit()
            db.refresh(update_turnover)

    return True
