import os
import logging
from fastapi import FastAPI, Request
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
        application = Application.builder().token(TOKEN).build()
        
        # Add handlers
        application.add_handler(CommandHandler("start", start_command))
        logger.info("Added command handlers")
        
        logger.info("Application startup complete!")
    except Exception as e:
        logger.error(f"Startup error: {e}", exc_info=True)
        raise

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

@app.post("/webhook")
async def webhook(request: Request):
    """Handle webhook updates"""
    try:
        # Log request details
        logger.info("Webhook called")
        logger.info(f"Headers: {request.headers}")
        
        # Get and log request body
        body = await request.body()
        logger.info(f"Raw body: {body}")
        
        # Parse JSON
        data = await request.json()
        logger.info(f"Parsed data: {data}")
        
        # Create update object
        update = Update.de_json(data, bot)
        if update:
            logger.info(f"Created Update object: {update}")
            await application.process_update(update)
            logger.info("Update processed")
        
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
        forwarded_allow_ips="*"
    )
