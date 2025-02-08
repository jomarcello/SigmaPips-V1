# Market opties met hun instrumenten
MARKETS = {
    "forex": {
        "name": "Forex",
        "instruments": ["EURUSD", "GBPUSD", "USDJPY", "AUDUSD", "USDCAD"]
    },
    "crypto": {
        "name": "Crypto",
        "instruments": ["BTCUSD", "ETHUSD", "XRPUSD", "ADAUSD", "SOLUSD"]
    },
    "commodities": {
        "name": "Commodities",
        "instruments": ["XAUUSD", "XAGUSD", "WTIUSD", "XCUUSD", "NATGAS"]
    },
    "indices": {
        "name": "Indices",
        "instruments": ["SPX500", "NAS100", "US30", "GER40", "UK100"]
    }
}

# Timeframes
TIMEFRAMES = ["15m", "1h", "4h"] 