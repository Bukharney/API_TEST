from settrade_v2 import Investor


def login():
    investor = Investor(
        app_id="NT8ff5aBQMXwpzTe",
        app_secret="SVJ8Mz4ZnZJqvrMEHJH8t41nZp7/UlSqqwcksc04eq8=",
        broker_id="SANDBOX",
        app_code="SANDBOX",
        is_auto_queue=False,
    )
    return investor


def get_quote_symbol(symbol: str):
    investor = login()
    if not investor:
        return "Error"
    mkt_data = investor.MarketData()
    res = mkt_data.get_quote_symbol(symbol)
    return res


def get_candlestick(symbol: str, interval: str, limit: int):
    investor = login()
    mkt_data = investor.MarketData()
    res = mkt_data.get_candlestick(
        symbol=symbol,
        interval=interval,
        limit=limit,
    )
    return res
