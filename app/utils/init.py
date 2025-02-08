from telegram import Update, Bot
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    ContextTypes,
    CallbackQueryHandler
)
import os
import redis
from supabase import create_client
import logging

logger = logging.getLogger(__name__)

async def init_redis():
    """Initialize Redis connection"""
    global redis_client
    try:
        redis_client = redis.Redis(
            host=os.getenv('REDIS_HOST', 'redis'),
            port=int(os.getenv('REDIS_PORT', 6379)),
            decode_responses=True
        )
        redis_client.ping()
        logger.info("✅ Redis connection successful")
    except Exception as e:
        logger.error(f"❌ Redis connection failed: {str(e)}")
        redis_client = None

async def init_supabase():
    """Initialize Supabase connection"""
    global supabase
    try:
        url = os.getenv('SUPABASE_URL')
        key = os.getenv('SUPABASE_KEY')
        
        if not url or not key:
            raise ValueError("Missing Supabase credentials")
            
        supabase = create_client(url, key)
        
        # Test connection
        test_response = supabase.table("subscriber_preferences").select("count").execute()
        logger.info("✅ Supabase connection successful")
            
    except Exception as e:
        logger.error(f"❌ Supabase connection failed: {str(e)}", exc_info=True)
        supabase = None

async def init_bot():
    """Initialize Telegram bot"""
    global bot
    try:
        token = os.getenv('TELEGRAM_BOT_TOKEN')
        if not token:
            raise ValueError("Missing bot token")
        bot = ApplicationBuilder().token(token).build()
        await bot.initialize()
        bot_info = await bot.bot.get_me()
        logger.info(f"✅ Bot connected successfully: @{bot_info.username}")
        return True
    except Exception as e:
        logger.error(f"❌ Bot initialization failed: {str(e)}")
        return False

async def register_handlers():
    """Register all bot handlers"""
    from app.bot.handlers import (
        start_command,
        help_command,
        button_callback,
        error_handler
    )
    
    try:
        # Error handler
        bot.add_error_handler(error_handler)
        
        # Command handlers
        bot.add_handler(CommandHandler("start", start_command))
        bot.add_handler(CommandHandler("help", help_command))
        
        # Callback handler voor inline knoppen
        bot.add_handler(CallbackQueryHandler(button_callback))
        
        logger.info("✅ Bot handlers registered successfully")
    except Exception as e:
        logger.error(f"❌ Error registering handlers: {str(e)}", exc_info=True) 