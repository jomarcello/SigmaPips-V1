from fastapi import FastAPI, HTTPException
from telegram.ext import Application
from supabase import create_client
from redis import Redis
from dotenv import load_dotenv
import os
from app.bot.handlers import register_handlers
from app.utils.logger import logger
from app.services.signal_processor.processor import SignalProcessor
from app.services.signal_processor.models import TradingSignal
from app.services.sentiment.analyzer import SentimentAnalyzer
from app.config import Config
import logging

# Load environment variables
load_dotenv()
logger.info("Environment variables loaded")

# Initialize FastAPI
app = FastAPI(title="TradingBot API")
logger.info("FastAPI initialized")

# Initialize Supabase
try:
    supabase = create_client(
        os.getenv("SUPABASE_URL"),
        os.getenv("SUPABASE_KEY")
    )
    logger.info("Supabase client initialized")
except Exception as e:
    logger.error(f"Failed to initialize Supabase: {str(e)}")

# Initialize Redis
try:
    redis_client = Redis.from_url(os.getenv("REDIS_URL"))
    logger.info("Redis client initialized")
except Exception as e:
    logger.error(f"Failed to initialize Redis: {str(e)}")

# Initialize Telegram Bot
try:
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    logger.debug(f"Using bot token: {token[:5]}...{token[-5:]}")
    
    telegram_app = Application.builder().token(token).build()
    logger.info("Telegram bot initialized")
except Exception as e:
    logger.error(f"Failed to initialize Telegram bot: {str(e)}", exc_info=True)
    raise

# Register bot handlers
register_handlers(telegram_app)

# Initialize services
signal_processor = SignalProcessor()
analyzer = SentimentAnalyzer()

@app.get("/")
async def root():
    logger.debug("Health check endpoint called")
    return {"status": "online"}

@app.post("/webhook/tradingview")
async def tradingview_webhook(data: dict):
    """Handle incoming webhooks from TradingView"""
    try:
        signal = await signal_processor.process_tradingview_webhook(data)
        return {"status": "success", "message": "Signal processed successfully"}
    except Exception as e:
        logger.error(f"Error processing webhook: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

# Start the bot
@app.on_event("startup")
async def startup_event():
    """Start the bot when the API starts"""
    logger.info("Starting application...")
    try:
        # Test bot connection
        bot = telegram_app.bot
        me = await bot.get_me()
        logger.info(f"Bot connection successful - @{me.username} ({me.first_name})")
        
        # Initialize and start bot with polling
        await telegram_app.initialize()
        await telegram_app.start()
        await telegram_app.updater.start_polling()
        logger.info("🤖 Telegram bot started successfully and polling for updates!")
    except Exception as e:
        logger.error(f"Failed to start Telegram bot: {str(e)}", exc_info=True)
        raise

@app.on_event("shutdown")
async def shutdown_event():
    """Stop the bot when the API stops"""
    logger.info("Shutting down application...")
    try:
        await telegram_app.stop()
        logger.info("🤖 Telegram bot stopped successfully!")
    except Exception as e:
        logger.error(f"Error during shutdown: {str(e)}")

@app.post("/analyze")
async def analyze_sentiment(data: dict):
    """Analyze market sentiment for given symbol"""
    try:
        symbol = data.get('symbol')
        if not symbol:
            raise HTTPException(status_code=400, detail="Symbol is required")
            
        analysis = await analyzer.analyze(symbol)
        return {"symbol": symbol, "sentiment": analysis}
        
    except Exception as e:
        logger.error(f"Error analyzing sentiment: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health_check():
    logger.info("Health check called")
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5000) 