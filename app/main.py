import os
import logging
from fastapi import FastAPI, Request
from telegram.ext import ApplicationBuilder, CommandHandler
from dotenv import load_dotenv
from telegram import Update

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
    try:
        data = await request.json()
        logger.info(f"Received webhook update: {data}")
        
        # Log meer details
        logger.info("Converting update to object...")
        update = Update.de_json(data, application.bot)
        logger.info(f"Update object created: {update}")
        
        logger.info("Processing update...")
        await application.process_update(update)
        logger.info("Update processed successfully")
        
        return {"ok": True}
    except Exception as e:
        logger.error(f"Error in webhook handler: {str(e)}", exc_info=True)
        # Log de volledige stacktrace
        import traceback
        logger.error(traceback.format_exc())
        return {"ok": False, "error": str(e)}

@app.on_event("startup")
async def startup_event():
    """Start the bot when the FastAPI app starts"""
    try:
        logger.info("Starting bot...")
        await application.initialize()
        
        # Delete existing webhook first
        logger.info("Deleting existing webhook...")
        await application.bot.delete_webhook()
        
        # Set new webhook URL with allowed updates
        webhook_url = "https://sigmapips-v1-production.up.railway.app/webhook"
        logger.info(f"Setting webhook to {webhook_url}")
        
        result = await application.bot.set_webhook(
            url=webhook_url,
            allowed_updates=['message', 'callback_query'],
            drop_pending_updates=True  # Dit verwijdert oude updates
        )
        
        if result:
            logger.info("Webhook setup successful!")
        else:
            logger.error("Webhook setup failed!")
        
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
    try:
        user = update.effective_user
        logger.info(f"Processing /start command from user {user.id}")
        
        message = await update.message.reply_text('Bot is running! 🚀')
        logger.info(f"Start message sent: {message.message_id}")
        
    except Exception as e:
        logger.error(f"Error in start command: {str(e)}", exc_info=True)
        await update.message.reply_text("Sorry, something went wrong!")

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=port)
