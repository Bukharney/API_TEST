from settrade_v2 import Investor


def login():
    investor = Investor(
        app_id="x878HsmA5yuk5XXR",
        app_secret="Yp5VyFlBxTgmljVkAmxOUpJDfmq9iESD+RE469PjMU8=",
        broker_id="SANDBOX",
        app_code="SANDBOX",
        is_auto_queue=False,
    )
    return investor


def get_quote_symbol(symbol: str):
    investor = login()
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
