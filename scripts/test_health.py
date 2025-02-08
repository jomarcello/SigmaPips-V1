import requests
import json

def check_services():
    """Test alle services"""
    services = {
        "signal": "https://signal-processor-production.up.railway.app/health",
        "telegram": "https://telegram-service-production-592d.up.railway.app/health",
        "news": "https://news-ai-service-production.up.railway.app/health",
        "subscriber": "https://subscriber-matcher-production.up.railway.app/health"
    }
    
    print("\n🔍 Checking services health...")
    
    for name, url in services.items():
        try:
            response = requests.get(url, verify=False)
            status = response.status_code
            print(f"\n{name.upper()} Service:")
            print(f"Status Code: {status}")
            print(f"Response: {json.dumps(response.json(), indent=2)}")
            print(f"Status: {'✅' if status == 200 else '❌'}")
        except Exception as e:
            print(f"\n{name.upper()} Service:")
            print(f"Error: ❌ {str(e)}")

if __name__ == "__main__":
    check_services() 