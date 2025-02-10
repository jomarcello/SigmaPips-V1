# Market opties met hun instrumenten
MARKETS = {
    "forex": {
        "name": "Forex",
        "instruments": ["EURUSD", "GBPUSD", "USDJPY", "AUDUSD", "USDCAD"]
    },
    "crypto": {
        "name": "Crypto",
        "instruments": ["BTCUSDT", "ETHUSDT", "BNBUSDT"]
    },
    "commodities": {
        "name": "Commodities",
        "instruments": ["XAUUSD", "XAGUSD", "WTIUSD"]
    },
    "indices": {
        "name": "Indices",
        "instruments": ["US30", "SPX500", "NASDAQ"]
    }
}

# Timeframes
TIMEFRAMES = ["15m", "1h", "4h"] 