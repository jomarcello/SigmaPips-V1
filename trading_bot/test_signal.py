import requests
import json

def test_signal():
    url = "http://localhost:7000/signal"
    
    signal = {
        "symbol": "EURUSD",
        "action": "BUY",
        "price": "1.0950",
        "stopLoss": "1.0900",
        "takeProfit": "1.1000",
        "interval": "1h",
        "strategy": "Price Action Breakout"
    }
    
    response = requests.post(url, json=signal)
    print(f"Status Code: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")

if __name__ == "__main__":
    test_signal() 