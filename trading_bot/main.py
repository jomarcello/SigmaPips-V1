from fastapi import FastAPI, HTTPException, Request
import logging
import os
from typing import Dict, Any
import asyncio
from redis import Redis

from services.telegram_service import TelegramService
from services.news_ai_service import NewsAIService
from services.chart_service import ChartService
from services.calendar_service import CalendarService
from database import Database

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()

# Initialize services
db = Database()
telegram = TelegramService(db)
news_ai = NewsAIService(db)
chart = ChartService()
calendar = CalendarService(db)

# Update Redis configuratie
redis_client = Redis(
    host=os.getenv('REDIS_HOST', 'redis'),
    port=int(os.getenv('REDIS_PORT', 6379)),
    decode_responses=True
)

@app.get("/health")
async def health_check():
    """Health check endpoint voor Railway"""
    return {"status": "healthy"}

@app.post("/signal")
async def process_signal(signal: Dict[str, Any]):
    """Process trading signal"""
    try:
        # 1. Match subscribers
        subscribers = await db.match_subscribers(signal)
        
        # 2. Get market analysis
        sentiment = await news_ai.analyze_sentiment(signal["symbol"])
        chart_image = await chart.generate_chart(signal["symbol"], signal["interval"])
        calendar_events = await calendar.get_relevant_events(signal["symbol"])
        
        # 3. Send to subscribers
        tasks = []
        for subscriber in subscribers:
            tasks.append(
                telegram.send_signal(
                    chat_id=subscriber["chat_id"],
                    signal=signal,
                    sentiment=sentiment,
                    chart=chart_image,
                    events=calendar_events
                )
            )
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        return {"status": "success", "sent_to": len(results)}
        
    except Exception as e:
        logger.error(f"Error processing signal: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/webhook")
async def webhook(request: Request):
    """Handle TradingView webhook and Telegram updates"""
    try:
        payload = await request.json()
        
        # Check if this is a callback query
        if 'callback_query' in payload:
            return await telegram.handle_callback_query(payload['callback_query'])
            
        # Check if this is a Telegram message
        if 'message' in payload and 'text' in payload['message']:
            return await handle_telegram_command(payload['message'])
            
        # Otherwise treat it as a trading signal
        return await process_signal(payload)
        
    except Exception as e:
        logger.error(f"Webhook error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

async def handle_telegram_command(message: Dict[str, Any]):
    """Handle Telegram bot commands"""
    try:
        command = message['text']
        chat_id = message['chat']['id']
        
        if command == '/start':
            return await telegram.send_welcome_message(chat_id)
            
        return {"status": "unknown_command"}
        
    except Exception as e:
        logger.error(f"Error handling command: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=int(os.getenv("PORT", 5000))) 