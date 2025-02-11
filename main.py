from fastapi import FastAPI, HTTPException
import logging
import os
from typing import Dict, Any
import asyncio

from services.telegram_service import TelegramService
from services.news_ai_service import NewsAIService
from services.chart_service import ChartService
from services.calendar_service import CalendarService
from services.database import Database

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()
port = int(os.getenv("PORT", 8080))

# Initialize services
db = Database(
    url=os.getenv("SUPABASE_URL"),
    key=os.getenv("SUPABASE_KEY")
)
telegram = TelegramService(
    token=os.getenv("TELEGRAM_BOT_TOKEN"),
    db=db
)
news_ai = NewsAIService(db)
chart = ChartService()
calendar = CalendarService(db)

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

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=port) 