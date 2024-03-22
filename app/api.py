import time
from settrade_v2 import Investor


class SetTradeSymbol:
    def __init__(self):
        self.investor = Investor(
            app_id="YfTh3KaFsv1ugv3Z",
            app_secret="PolUag6rQw3tzfmvlcj2QkVG4Ilazq+T7S4oubDfwyQ=",
            broker_id="SANDBOX",
            app_code="SANDBOX",
            is_auto_queue=False,
        )

    def get_quote_symbol(self, symbol: str):
        mkt_data = self.investor.MarketData()
        res = mkt_data.get_quote_symbol(symbol)
        return res

    def get_candlestick(self, symbol: str, interval: str, limit: int):
        mkt_data = self.investor.MarketData()
        res = mkt_data.get_candlestick(
            symbol=symbol,
            interval=interval,
            limit=limit,
        )
        return res

    def get_candlesticks(self, symbols, interval: str, limit: int):
        mkt_data = self.investor.MarketData()
        for symbol in symbols:
            res = mkt_data.get_candlestick(
                symbol=symbol.symbol,
                interval=interval,
                limit=limit,
            )
            symbol.close = format(res["close"][0], ".2f")
            symbol.open = format(res["open"][0], ".2f")
            symbol.change = format(res["close"][0] - res["open"][0], ".2f")
            symbol.value = res["value"][0]

        return res

    def get_price_info(self, symbol: str):
        realtime = self.investor.RealtimeDataConnection()
        data1 = {}

        def my_message(result):
            nonlocal data1
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
            data1 = {key: result.get(key) for key in keys}

        sub = realtime.subscribe_price_info(symbol, on_message=my_message)
        sub.start()

        mkt_data = self.investor.MarketData()
        data2 = mkt_data.get_candlestick(
            symbol=symbol,
            interval="1d",
            limit=1,
            normalized=True,
        )

        data1["open"] = data2["open"][0]
        data1["close"] = data2["close"][0]

        time.sleep(1)

        return data1

    def get_bid_offer(self, symbol: str):
        realtime = self.investor.RealtimeDataConnection()
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

    def get_market_data(self, symbol: str):
        realtime = self.investor.RealtimeDataConnection()

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

        mkt_data = self.investor.MarketData()
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


if __name__ == "__main__":
    st = SetTradeSymbol()
