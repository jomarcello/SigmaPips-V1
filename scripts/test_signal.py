import requests
import json

def test_all_services():
    """Test alle services en stuur een signaal"""
    
    # 1. Check health van alle services
    services = {
        "signal": "http://localhost:5005/health",  # Signal processor
        "ai": "http://localhost:5001/health",      # AI signal service
        "telegram": "http://localhost:5000/health",
        "chart": "http://localhost:5002/health",
        "news": "http://localhost:5001/health",
        "calendar": "http://localhost:5003/health"
    }
    
    print("\n🔍 Checking services health...")
    for name, url in services.items():
        try:
            response = requests.get(url)
            print(f"{name}: {'✅' if response.status_code == 200 else '❌'}")
        except Exception as e:
            print(f"{name}: ❌ ({str(e)})")

    # 2. Stuur een test signaal
    print("\n📨 Sending test signal...")
    signal = {
        "symbol": "EURUSD",
        "action": "BUY",
        "price": "1.0950",
        "stopLoss": "1.0930",
        "takeProfit": "1.0980",
        "interval": "15m",
        "strategy": "MA Crossover"
    }
    
    try:
        # Stuur naar signal processor
        response = requests.post(
            "http://localhost:5005/signal",
            json=signal
        )
        print(f"\nSignal Response: {json.dumps(response.json(), indent=2)}")
        
        if response.status_code == 200:
            print("\n✅ Signal sent successfully!")
            print("\nAI Analysis:")
            print(response.json().get('aiAnalysis', 'No AI analysis available'))
            
    except Exception as e:
        print(f"Error sending signal: {str(e)}")

if __name__ == "__main__":
    test_all_services() 