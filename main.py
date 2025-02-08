import os
import asyncio
import logging
from dotenv import load_dotenv
from services.telegram_service.bot import TelegramService
from services.news_ai_service.sentiment import NewsAIService
from services.database.db import Database

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

async def main():
    try:
        # Load environment variables
        load_dotenv()
        
        # Initialize services
        db = Database()
        news_service = NewsAIService(db)
        telegram_service = TelegramService(db)
        
        # Test connections
        logger.info("Testing services...")
        
        # Keep the bot running
        logger.info("Bot is running...")
        await asyncio.Event().wait()
        
    except Exception as e:
        logger.error(f"Error in main: {str(e)}", exc_info=True)

if __name__ == "__main__":
    asyncio.run(main()) 