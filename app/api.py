import datetime
import time
from settrade_v2 import Investor


def login():
    investor = Investor(
        app_id="mh6I0FhNzB3Lx6Nf",
        app_secret="AIigoP9qSNe2vIyoX83iNWp3rLAfcxzDjYUSbNi4uwUt",
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
    time.sleep(1)
    investor = login()
    mkt_data = investor.MarketData()
    res = mkt_data.get_candlestick(
        symbol=symbol,
        interval=interval,
        limit=limit,
    )
    return res


def get_price_info(symbol: str):
    time.sleep(1)
    investor = login()
    realtime = investor.RealtimeDataConnection()
    data = {}

    def my_message(result):
        nonlocal data
        result = result.get("data", {})
        keys = [
            "symbol",
            "high",
            "low",
            "last",
            "total_volume",
            "projected_open_price",
            "change",
            "total_value",
            "market_status",
        ]
        data = {key: result.get(key) for key in keys}

    sub = realtime.subscribe_price_info(symbol, on_message=my_message)
    sub.start()
    time.sleep(1)
    return data


def get_bid_offer(symbol: str):
    investor = login()
    realtime = investor.RealtimeDataConnection()
    data = {}

    def my_message(result):
        nonlocal data
        result = result.get("data", {})
        keys = [
            "symbol",
            "bid_flag",
            "ask_flag",
            "ask_price1",
            "ask_price2",
            "ask_price3",
            "ask_price4",
            "ask_price5",
            "ask_price6",
            "ask_price7",
            "ask_price8",
            "ask_price9",
            "ask_price10",
            "ask_volume1",
            "ask_volume2",
            "ask_volume3",
            "ask_volume4",
            "ask_volume5",
            "ask_volume6",
            "ask_volume7",
            "ask_volume8",
            "ask_volume9",
            "ask_volume10",
            "bid_price1",
            "bid_price2",
            "bid_price3",
            "bid_price4",
            "bid_price5",
            "bid_price6",
            "bid_price7",
            "bid_price8",
            "bid_price9",
            "bid_price10",
            "bid_volume1",
            "bid_volume2",
            "bid_volume3",
            "bid_volume4",
            "bid_volume5",
            "bid_volume6",
            "bid_volume7",
            "bid_volume8",
            "bid_volume9",
            "bid_volume10",
        ]
        data = {key: result.get(key) for key in keys}

    sub = realtime.subscribe_bid_offer(symbol, on_message=my_message)
    sub.start()
    time.sleep(1)
    return data


def get_market_data(symbol: str):
    investor = login()
    realtime = investor.RealtimeDataConnection()

    data1 = {}

    def func1(result):
        nonlocal data1
        result = result.get("data", {})
        keys = [
            "symbol",
            "bid_flag",
            "ask_flag",
            "ask_price1",
            "ask_price2",
            "ask_price3",
            "ask_price4",
            "ask_price5",
            "ask_price6",
            "ask_price7",
            "ask_price8",
            "ask_price9",
            "ask_price10",
            "ask_volume1",
            "ask_volume2",
            "ask_volume3",
            "ask_volume4",
            "ask_volume5",
            "ask_volume6",
            "ask_volume7",
            "ask_volume8",
            "ask_volume9",
            "ask_volume10",
            "bid_price1",
            "bid_price2",
            "bid_price3",
            "bid_price4",
            "bid_price5",
            "bid_price6",
            "bid_price7",
            "bid_price8",
            "bid_price9",
            "bid_price10",
            "bid_volume1",
            "bid_volume2",
            "bid_volume3",
            "bid_volume4",
            "bid_volume5",
            "bid_volume6",
            "bid_volume7",
            "bid_volume8",
            "bid_volume9",
            "bid_volume10",
        ]
        data1 = {key: result.get(key) for key in keys}

    sub1 = realtime.subscribe_bid_offer(symbol, on_message=func1)
    sub1.start()

    data2 = {}

    def func2(result):
        nonlocal data2
        result = result.get("data", {})
        keys = [
            "symbol",
            "high",
            "low",
            "last",
            "total_volume",
            "projected_open_price",
            "change",
            "total_value",
            "market_status",
        ]
        data2 = {key: result.get(key) for key in keys}

    sub2 = realtime.subscribe_price_info(symbol, on_message=func2)
    sub2.start()

    mkt_data = investor.MarketData()
    data3 = mkt_data.get_candlestick(
        symbol=symbol,
        interval="1d",
        limit=1,
        normalized=True,
    )

    data4 = mkt_data.get_candlestick(
        symbol=symbol,
        interval="1d",
        limit=60,
        normalized=True,
    )

    data5 = mkt_data.get_quote_symbol(symbol)
    time.sleep(1)

    return {
        "bid_offer": data1,
        "price_info": data2,
        "candlestick_1limit": data3,
        "candlestick_50limit": data4,
        "quote_symbol": data5,
    }
