import os
import logging
from fastapi import FastAPI, Request, BackgroundTasks
from telegram import Bot, Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters
from app.bot.constants import MARKETS
from app.utils.supabase import supabase

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
        application.add_handler(CommandHandler("help", help_command))
        application.add_handler(CommandHandler("status", status_command))
        application.add_handler(CallbackQueryHandler(button_callback))
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
    user = update.effective_user
    
    # Show market selection
    keyboard = [
        [InlineKeyboardButton(market_data["name"], callback_data=f"market_{market_id}")]
        for market_id, market_data in MARKETS.items()
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        f"Welcome {user.first_name}! 👋\n\n"
        "Please select a market to receive trading signals:",
        reply_markup=reply_markup
    )

async def help_command(update: Update, context):
    """Handle /help command"""
    await update.message.reply_text(
        "🤖 TradingBot Help:\n\n"
        "Commands:\n"
        "/start - Start the bot\n"
        "/help - Show this help message\n"
        "/status - Check bot status"
    )

async def status_command(update: Update, context):
    """Handle /status command"""
    await update.message.reply_text("✅ Bot is online and active!")

async def button_callback(update: Update, context):
    """Handle button callbacks"""
    query = update.callback_query
    logger.debug(f"Received callback query: {query.data}")
    
    try:
        await query.answer()
        
        if query.data.startswith("market_"):
            market_id = query.data.replace("market_", "")
            if market_id in MARKETS:
                market = MARKETS[market_id]
                keyboard = [
                    [InlineKeyboardButton(instrument, callback_data=f"instrument_{market_id}_{instrument}")]
                    for instrument in market["instruments"]
                ]
                # Add back button
                keyboard.append([InlineKeyboardButton("🔙 Back to Markets", callback_data="back_to_markets")])
                reply_markup = InlineKeyboardMarkup(keyboard)
                await query.message.edit_text(
                    f"Select an instrument from {market['name']}:",
                    reply_markup=reply_markup
                )
        
        elif query.data.startswith("instrument_"):
            # Show timeframe selection
            _, market_id, instrument = query.data.split("_", 2)
            
            keyboard = [
                [InlineKeyboardButton(tf, callback_data=f"timeframe_{market_id}_{instrument}_{tf}")]
                for tf in ["15m", "1h", "4h"]
            ]
            keyboard.append([InlineKeyboardButton("🔙 Back to Instruments", callback_data=f"market_{market_id}")])
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await query.message.edit_text(
                f"Select a timeframe for {instrument}:",
                reply_markup=reply_markup
            )
        
        elif query.data.startswith("timeframe_"):
            # Process the complete selection
            _, market_id, instrument, timeframe = query.data.split("_", 3)
            user_id = str(query.from_user.id)  # Convert to string for Supabase
            
            # Save to Supabase
            data = {
                "user_id": user_id,
                "market": market_id,
                "instrument": instrument,
                "timeframe": timeframe,
                "created_at": "now()"  # Add timestamp
            }
            
            try:
                # Check for duplicates
                response = supabase.table("signal_preferences").select("*").eq(
                    "user_id", user_id
                ).eq("market", market_id).eq("instrument", instrument).eq(
                    "timeframe", timeframe
                ).execute()
                
                logger.debug(f"Supabase duplicate check response: {response}")
                
                if not response.data:  # No duplicate found
                    result = supabase.table("signal_preferences").insert(data).execute()
                    logger.info(f"Saved preference to Supabase: {result}")
                    
                    keyboard = [
                        [
                            InlineKeyboardButton("➕ Add Another", callback_data="back_to_markets"),
                            InlineKeyboardButton("📋 My Preferences", callback_data="view_preferences")
                        ]
                    ]
                    reply_markup = InlineKeyboardMarkup(keyboard)
                    
                    await query.message.edit_text(
                        f"✅ Preference saved!\n\n"
                        f"Market: {MARKETS[market_id]['name']}\n"
                        f"Instrument: {instrument}\n"
                        f"Timeframe: {timeframe}",
                        reply_markup=reply_markup
                    )
                else:
                    keyboard = [[InlineKeyboardButton("🔙 Back to Markets", callback_data="back_to_markets")]]
                    reply_markup = InlineKeyboardMarkup(keyboard)
                    await query.message.edit_text(
                        "⚠️ This preference already exists!\n"
                        "Please choose a different combination.",
                        reply_markup=reply_markup
                    )
            except Exception as e:
                logger.error(f"Supabase error: {str(e)}", exc_info=True)
                raise
        
        elif query.data == "back_to_markets":
            keyboard = [
                [InlineKeyboardButton(market_data["name"], callback_data=f"market_{market_id}")]
                for market_id, market_data in MARKETS.items()
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await query.message.edit_text(
                "Please select a market to receive trading signals:",
                reply_markup=reply_markup
            )
            
        elif query.data == "view_preferences":
            # Show user preferences
            response = supabase.table("signal_preferences").select("*").eq(
                "user_id", query.from_user.id
            ).execute()
            
            if response.data:
                text = "📋 Your signal preferences:\n\n"
                for i, pref in enumerate(response.data, 1):
                    text += f"{i}. {pref['market'].upper()} - {pref['instrument']} ({pref['timeframe']})\n"
                
                keyboard = []
                for i, pref in enumerate(response.data, 1):
                    keyboard.append([
                        InlineKeyboardButton(
                            f"🗑️ Delete #{i}", 
                            callback_data=f"delete_preference_{pref['id']}"
                        )
                    ])
                
                keyboard.append([InlineKeyboardButton("➕ Add More", callback_data="back_to_markets")])
                reply_markup = InlineKeyboardMarkup(keyboard)
                
                await query.message.edit_text(text, reply_markup=reply_markup)
            else:
                await query.message.edit_text(
                    "You don't have any signal preferences yet.",
                    reply_markup=InlineKeyboardMarkup([[
                        InlineKeyboardButton("➕ Add Preferences", callback_data="back_to_markets")
                    ]])
                )
                
    except Exception as e:
        logger.error(f"Error in button callback: {str(e)}", exc_info=True)
        await query.message.edit_text(
            "❌ An error occurred. Please try again.",
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton("🔙 Back to Markets", callback_data="back_to_markets")
            ]])
        )

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

async def echo_message(update: Update, context):
    """Echo the user message."""
    await update.message.reply_text(update.message.text)

@app.post("/send_test_signal")
async def send_test_signal():
    """Send a test signal to subscribers"""
    try:
        # Haal alle preferences op uit Supabase
        response = supabase.table("signal_preferences").select("*").execute()
        logger.info(f"Found {len(response.data)} preferences")
        
        if not response.data:
            return {"message": "No subscribers found"}
            
        # Test signaal
        signal = {
            "market": "forex",
            "instrument": "EURUSD",
            "timeframe": "15m",
            "direction": "BUY",
            "entry": "1.0750",
            "sl": "1.0720",
            "tp": "1.0800",
            "reason": "Test signal - Price broke above resistance"
        }
        
        # Stuur naar alle subscribers die dit instrument volgen
        sent_count = 0
        for pref in response.data:
            if (pref["market"] == signal["market"] and 
                pref["instrument"] == signal["instrument"] and 
                pref["timeframe"] == signal["timeframe"]):
                
                message = (
                    f"🚨 NEW SIGNAL ALERT!\n\n"
                    f"📊 {signal['instrument']} ({signal['timeframe']})\n"
                    f"📈 Action: {signal['direction']}\n"
                    f"⚡️ Entry: {signal['entry']}\n"
                    f"🛑 Stop Loss: {signal['sl']}\n"
                    f"🎯 Take Profit: {signal['tp']}\n\n"
                    f"📝 Analysis:\n{signal['reason']}"
                )
                
                await bot.send_message(
                    chat_id=int(pref["user_id"]),  # Convert string to int
                    text=message
                )
                sent_count += 1
                logger.info(f"Signal sent to user {pref['user_id']}")
                
        return {
            "message": f"Test signal sent to {sent_count} subscribers",
            "signal": signal
        }
        
    except Exception as e:
        logger.error(f"Error sending test signal: {str(e)}", exc_info=True)
        return {"error": str(e)}

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
