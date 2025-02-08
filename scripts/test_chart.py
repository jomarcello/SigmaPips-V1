import requests
import json

def test_chart():
    url = "http://localhost:5002/chart/bytes"
    
    data = {
        "symbol": "EURUSD",
        "timeframe": "15m"
    }
    
    response = requests.post(url, json=data)
    
    # Save chart image
    if response.status_code == 200:
        with open("test_chart.png", "wb") as f:
            f.write(response.content)
        print("Chart saved as test_chart.png")
    else:
        print(f"Error: {response.text}")

if __name__ == "__main__":
    test_chart() 