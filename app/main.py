import os
import logging
from fastapi import FastAPI, Request, BackgroundTasks
from telegram import Bot, Update
from telegram.ext import Application, CommandHandler

# Set up logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.DEBUG
)
logger = logging.getLogger(__name__)

# Initialize FastAPI
app = FastAPI()

# Startup event
@app.on_event("startup")
async def startup_event():
    """Run on application startup"""
    try:
        logger.info("Starting application...")
        
        # Initialize bot
        global bot, application
        TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
        if not TOKEN:
            raise ValueError("No TELEGRAM_BOT_TOKEN found in environment")
            
        logger.info("Initializing bot...")
        bot = Bot(TOKEN)
        await bot.initialize()  # Initialize bot first
        
        # Initialize application
        logger.info("Initializing application...")
        application = Application.builder().token(TOKEN).build()
        await application.initialize()
        
        # Add handlers
        application.add_handler(CommandHandler("start", start_command))
        logger.info("Added command handlers")
        
        # Start application
        logger.info("Starting application...")
        await application.start()
        logger.info("Application startup complete!")
        
    except Exception as e:
        logger.error(f"Startup error: {e}", exc_info=True)
        raise

@app.on_event("shutdown")
async def shutdown_event():
    """Run on application shutdown"""
    try:
        logger.info("Stopping application...")
        await application.stop()
        logger.info("Application stopped")
    except Exception as e:
        logger.error(f"Shutdown error: {e}", exc_info=True)

async def start_command(update: Update, context):
    """Handle /start command"""
    logger.info(f"Start command from user {update.effective_user.id}")
    await update.message.reply_text("Bot is working! 🚀")

@app.get("/")
async def root():
    """Root endpoint"""
    logger.info("Root endpoint called")
    return {"message": "API is running"}

@app.get("/health")
async def health():
    """Health check"""
    logger.info("Health check called")
    return {"status": "ok"}

async def process_telegram_update(data: dict):
    """Process Telegram update in background"""
    try:
        if update := Update.de_json(data, bot):
            await application.process_update(update)
            logger.info("Update processed successfully")
    except Exception as e:
        logger.error(f"Background task error: {e}", exc_info=True)

@app.post("/webhook")
async def webhook(request: Request):
    """Handle webhook updates"""
    try:
        # Log webhook call
        logger.info("Webhook called")
        
        # Get update data
        data = await request.json()
        logger.info(f"Received update: {data}")
        
        # Process update
        if update := Update.de_json(data, bot):
            await application.process_update(update)
            logger.info("Update processed successfully")
        
        return {"ok": True}
    except Exception as e:
        logger.error(f"Webhook error: {e}", exc_info=True)
        return {"ok": False, "error": str(e)}

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8080))
    logger.info(f"Starting server on port {port}")
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=port,
        log_level="debug",
        proxy_headers=True,
        forwarded_allow_ips="*",
        timeout_keep_alive=30,
        workers=1
    )
