import os
from fastapi import FastAPI
from telegram.ext import ApplicationBuilder, CommandHandler
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize FastAPI
app = FastAPI()

# Initialize Telegram bot
bot = ApplicationBuilder().token(os.getenv("TELEGRAM_BOT_TOKEN")).build()

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

@app.on_event("startup")
async def startup_event():
    """Start the bot when the FastAPI app starts"""
    # Start the bot
    await bot.initialize()
    await bot.start()
    
    # Add handlers
    bot.add_handler(CommandHandler("start", start_command))

@app.on_event("shutdown")
async def shutdown_event():
    """Stop the bot when the FastAPI app stops"""
    await bot.stop()

async def start_command(update, context):
    """Handle the /start command"""
    await update.message.reply_text('Bot is running! 🚀')

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=port)