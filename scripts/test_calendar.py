import requests
import json

def test_calendar():
    # Test basic calendar endpoint
    response = requests.get("http://localhost:5003/calendar")
    print("Calendar Events:")
    print(json.dumps(response.json(), indent=2))
    
    # Test impact filter
    response = requests.get("http://localhost:5003/calendar/impact/high")
    print("\nHigh Impact Events:")
    print(json.dumps(response.json(), indent=2))
    
    # Test currency filter
    response = requests.get("http://localhost:5003/calendar/currency/USD")
    print("\nUSD Events:")
    print(json.dumps(response.json(), indent=2))

if __name__ == "__main__":
    test_calendar() 