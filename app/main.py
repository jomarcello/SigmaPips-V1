import os
import logging
from fastapi import FastAPI, Request
from telegram.ext import ApplicationBuilder, CommandHandler
from dotenv import load_dotenv

# Set up logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Initialize FastAPI
app = FastAPI()

# Initialize Telegram bot
bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
logger.info(f"Initializing bot with token: {bot_token[:5]}...")  # Log alleen eerste 5 karakters voor veiligheid
application = ApplicationBuilder().token(bot_token).build()

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

@app.post("/webhook")
async def webhook(request: Request):
    """Handle incoming Telegram updates via webhook"""
    data = await request.json()
    logger.info(f"Received webhook update: {data}")
    await application.update_queue.put(data)
    return {"ok": True}

@app.on_event("startup")
async def startup_event():
    """Start the bot when the FastAPI app starts"""
    try:
        logger.info("Starting bot...")
        await application.initialize()
        
        # Set webhook URL
        webhook_url = "https://sigmapips-v1-production.up.railway.app/webhook"
        await application.bot.set_webhook(url=webhook_url)
        logger.info(f"Webhook set to {webhook_url}")
        
        # Add handlers
        application.add_handler(CommandHandler("start", start_command))
        logger.info("Added /start command handler")
        
        logger.info("Bot started successfully!")
    except Exception as e:
        logger.error(f"Error starting bot: {e}")
        raise

@app.on_event("shutdown")
async def shutdown_event():
    """Stop the bot when the FastAPI app stops"""
    logger.info("Stopping bot...")
    await application.stop()
    logger.info("Bot stopped!")

async def start_command(update, context):
    """Handle the /start command"""
    logger.info(f"Received /start command from user {update.effective_user.id}")
    await update.message.reply_text('Bot is running! 🚀')

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=port)
