import os
import sys
import asyncio
from dotenv import load_dotenv

# Add trading_bot directory to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from trading_bot.services.telegram_service.bot import TelegramService
from trading_bot.services.news_ai_service.sentiment import NewsAIService
from trading_bot.services.database.db import Database
from trading_bot.utils.logging_config import setup_logging

# Setup logging
logger = setup_logging()

async def test_telegram():
    logger.info("=== Starting Telegram Service Test ===")
    try:
        db = Database()
        logger.debug("Database instance created")
        
        telegram = TelegramService(db)
        logger.debug("TelegramService instance created")
        
        test_signal = {
            "symbol": "EURUSD",
            "action": "BUY",
            "price": 1.0950,
            "stopLoss": 1.0900,
            "takeProfit": 1.1000,
            "timeframe": "1H"
        }
        logger.debug(f"Test signal prepared: {test_signal}")
        
        chat_id = os.getenv("TELEGRAM_CHAT_ID")
        if not chat_id:
            logger.error("TELEGRAM_CHAT_ID not found in environment")
            return
            
        logger.info(f"Attempting to send test signal to chat_id: {chat_id}")
        result = await telegram.send_signal(
            chat_id=chat_id,
            signal=test_signal,
            sentiment="Market sentiment is bullish due to recent economic data."
        )
        
        if result:
            logger.info("✅ Telegram test successful!")
        else:
            logger.error("❌ Telegram test failed!")
            
    except Exception as e:
        logger.exception("Error in Telegram test")

async def test_sentiment():
    logger.info("=== Starting News AI Service Test ===")
    try:
        db = Database()
        logger.debug("Database instance created")
        
        news = NewsAIService(db)
        logger.debug("NewsAIService instance created")
        
        logger.info("Requesting sentiment analysis for EURUSD")
        sentiment = await news.analyze_sentiment("EURUSD")
        
        if sentiment:
            logger.info(f"✅ Sentiment analysis successful: {sentiment}")
        else:
            logger.error("❌ Sentiment analysis failed!")
            
    except Exception as e:
        logger.exception("Error in sentiment test")

async def test_database():
    logger.info("=== Starting Database Service Test ===")
    try:
        db = Database()
        logger.debug("Database instance created")
        
        test_signal = {
            "symbol": "EURUSD",
            "timeframe": "1H"
        }
        logger.debug(f"Test signal prepared: {test_signal}")
        
        logger.info("Testing subscriber matching")
        subscribers = await db.match_subscribers(test_signal)
        logger.info(f"Found {len(subscribers)} matching subscribers")
        
        # Test caching
        logger.info("Testing cache functionality")
        await db.cache_sentiment("EURUSD", "Test sentiment")
        cached = await db.get_cached_sentiment("EURUSD")
        
        if cached == "Test sentiment":
            logger.info("✅ Cache test successful!")
        else:
            logger.error("❌ Cache test failed!")
            
    except Exception as e:
        logger.exception("Error in database test")

async def main():
    try:
        # Load environment variables
        load_dotenv()
        logger.info("Environment variables loaded")
        
        # Log environment info
        logger.info(f"TELEGRAM_BOT_TOKEN present: {'TELEGRAM_BOT_TOKEN' in os.environ}")
        logger.info(f"OPENAI_API_KEY present: {'OPENAI_API_KEY' in os.environ}")
        logger.info(f"SUPABASE_URL present: {'SUPABASE_URL' in os.environ}")
        
        # Run tests
        await test_database()
        await test_sentiment()
        await test_telegram()
        
    except Exception as e:
        logger.exception("Error in main")

if __name__ == "__main__":
    asyncio.run(main()) 