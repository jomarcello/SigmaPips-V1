import os
import asyncio
from telegram import Bot
from telegram.request import Request
import ssl
import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

async def test_connection():
    # SSL context zonder verificatie
    ssl_context = ssl.create_default_context()
    ssl_context.check_hostname = False
    ssl_context.verify_mode = ssl.CERT_NONE
    
    request = Request(
        con_pool_size=8,
        connect_timeout=30.0,
        read_timeout=30.0,
        ssl_context=ssl_context,
        connection_pool_size=8
    )
    
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    if not token:
        logger.error("No TELEGRAM_BOT_TOKEN found in environment")
        return
        
    bot = Bot(token=token, request=request)
    
    try:
        me = await bot.get_me()
        logger.info(f"Successfully connected! Bot info: {me}")
        
        # Test een bericht versturen
        test_message = "🔧 Test bericht van de trading bot"
        chat_id = os.getenv("TELEGRAM_CHAT_ID")
        if chat_id:
            result = await bot.send_message(chat_id=chat_id, text=test_message)
            logger.info(f"Message sent! Message ID: {result.message_id}")
        else:
            logger.error("No TELEGRAM_CHAT_ID found in environment")
            
    except Exception as e:
        logger.error(f"Error during test: {str(e)}", exc_info=True)

if __name__ == "__main__":
    asyncio.run(test_connection()) 