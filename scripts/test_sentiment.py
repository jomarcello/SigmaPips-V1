import requests
import json

def test_sentiment():
    url = "http://localhost:5001/analyze"
    
    data = {
        "symbol": "EURUSD",
        "timeframe": "15m"
    }
    
    response = requests.post(url, json=data)
    print(f"Sentiment Analysis: {json.dumps(response.json(), indent=2)}")

if __name__ == "__main__":
    test_sentiment() 