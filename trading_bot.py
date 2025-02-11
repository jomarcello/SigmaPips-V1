from fastapi import FastAPI, Request, HTTPException
import os
import logging
import aiohttp
import asyncio
from typing import Dict, Any
from openai import AsyncOpenAI
import redis
from supabase import create_client

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()

# Initialize clients
openai_client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))
redis_client = redis.Redis(host=os.getenv("REDIS_HOST"), port=6379)
supabase = create_client(os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_KEY"))

class TradingBot:
    def __init__(self):
        self.telegram_token = os.getenv("TELEGRAM_BOT_TOKEN")
        
    async def match_subscribers(self, signal: Dict) -> List[str]:
        """Match signal with subscribers (previously Subscriber Matcher service)"""
        try:
            response = supabase.table("subscribers").select("*").execute()
            subscribers = response.data
            
            matched_subscribers = []
            for sub in subscribers:
                if self._matches_preferences(signal, sub):
                    matched_subscribers.append(sub["chat_id"])
                    
            return matched_subscribers
        except Exception as e:
            logger.error(f"Error matching subscribers: {str(e)}")
            return []
            
    async def analyze_sentiment(self, symbol: str) -> str:
        """Analyze market sentiment (previously News AI service)"""
        try:
            # Check cache first
            cache_key = f"sentiment:{symbol}"
            cached = redis_client.get(cache_key)
            if cached:
                return cached.decode()
                
            response = await openai_client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a market analyst."},
                    {"role": "user", "content": f"Analyze {symbol} sentiment briefly"}
                ]
            )
            
            sentiment = response.choices[0].message.content
            redis_client.setex(cache_key, 300, sentiment)  # Cache for 5 minutes
            return sentiment
            
        except Exception as e:
            logger.error(f"Error analyzing sentiment: {str(e)}")
            return "Sentiment analysis unavailable"
            
    async def send_telegram_message(self, chat_id: str, message: str):
        """Send Telegram message (previously Telegram service)"""
        try:
            url = f"https://api.telegram.org/bot{self.telegram_token}/sendMessage"
            async with aiohttp.ClientSession() as session:
                await session.post(url, json={
                    "chat_id": chat_id,
                    "text": message,
                    "parse_mode": "Markdown"
                })
        except Exception as e:
            logger.error(f"Error sending Telegram message: {str(e)}")

bot = TradingBot()

@app.post("/signal")
async def process_signal(signal: Dict[str, Any]):
    """Process trading signal"""
    try:
        # 1. Match subscribers
        chat_ids = await bot.match_subscribers(signal)
        
        # 2. Get sentiment
        sentiment = await bot.analyze_sentiment(signal["symbol"])
        
        # 3. Format message
        message = f"""
🔔 *TRADING SIGNAL*
Symbol: {signal['symbol']}
Action: {signal['action']}
Price: {signal['price']}
Stop Loss: {signal['stopLoss']}
Take Profit: {signal['takeProfit']}

📊 *SENTIMENT*
{sentiment}
"""
        
        # 4. Send to all matched subscribers
        tasks = []
        for chat_id in chat_ids:
            tasks.append(bot.send_telegram_message(chat_id, message))
            
        await asyncio.gather(*tasks)
        
        return {"status": "success", "sent_to": len(chat_ids)}
        
    except Exception as e:
        logger.error(f"Error processing signal: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=int(os.getenv("PORT", 5000))) 