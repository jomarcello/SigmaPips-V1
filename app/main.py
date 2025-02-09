import os
import logging
from fastapi import FastAPI, Request
from telegram import Update, Bot
from telegram.ext import Application, CommandHandler

# Set up logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.DEBUG  # Set to DEBUG for more info
)
logger = logging.getLogger(__name__)

# Initialize FastAPI
app = FastAPI()

# Initialize bot
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
bot = Bot(TOKEN)

@app.get("/health")
async def health():
    """Basic health check"""
    logger.info("Health check called")
    return {"status": "ok"}

@app.post("/webhook")
async def webhook(request: Request):
    """Simple webhook handler"""
    try:
        # Log the raw request
        body = await request.body()
        logger.info(f"Raw webhook body: {body}")
        
        # Parse JSON
        data = await request.json()
        logger.info(f"Parsed webhook data: {data}")
        
        # Try to send a message
        if 'message' in data and 'chat' in data['message']:
            chat_id = data['message']['chat']['id']
            logger.info(f"Sending message to chat_id: {chat_id}")
            
            await bot.send_message(
                chat_id=chat_id,
                text="Message received! 🚀"
            )
            logger.info("Message sent successfully")
            
        return {"ok": True}
    except Exception as e:
        logger.error(f"Webhook error: {e}", exc_info=True)
        return {"ok": False, "error": str(e)}

@app.on_event("startup")
async def startup():
    """Setup webhook on startup"""
    try:
        # Delete existing webhook
        logger.info("Deleting existing webhook...")
        await bot.delete_webhook()
        
        # Set new webhook
        webhook_url = "https://sigmapips-v1-production.up.railway.app/webhook"
        logger.info(f"Setting webhook to: {webhook_url}")
        
        result = await bot.set_webhook(webhook_url)
        if result:
            logger.info("Webhook setup successful!")
        else:
            logger.error("Webhook setup failed!")
            
    except Exception as e:
        logger.error(f"Startup error: {e}", exc_info=True)
        raise

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8080))
    logger.info(f"Starting server on port {port}")
    uvicorn.run(app, host="0.0.0.0", port=port)
