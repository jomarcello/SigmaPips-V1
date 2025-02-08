from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, InputMediaPhoto
from telegram.ext import ContextTypes, CommandHandler, MessageHandler, filters, CallbackContext, CallbackQueryHandler
from app.utils.logger import logger
from app.bot.constants import MARKETS, TIMEFRAMES
from app.utils.supabase import supabase
from app.services.chart.analyzer import ChartAnalyzer
from app.services.signal_processor.instance import signal_processor
from app.utils.redis import redis_client
import os
import aiohttp
from app.services.calendar.analyzer import EconomicCalendar

# Error handler toevoegen
async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Log Errors caused by Updates."""
    logger.error("Exception while handling an update:", exc_info=context.error)
    if update and isinstance(update, Update) and update.effective_message:
        await update.effective_message.reply_text("Sorry, er ging iets mis bij het verwerken van je bericht.")

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle the /start command"""
    logger.debug("Start command handler called")
    user = update.effective_user
    logger.info(f"Start command received from user {user.id} ({user.first_name})")
    
    # Show market selection directly
    keyboard = [
        [InlineKeyboardButton(market_data["name"], callback_data=f"market_{market_id}")]
        for market_id, market_data in MARKETS.items()
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    try:
        message = await update.message.reply_text(
            f"Welcome {user.first_name}! 👋\n\n"
            "Please select a market to receive trading signals:",
            reply_markup=reply_markup
        )
        logger.debug(f"Welcome message sent to user {user.id}: {message.message_id}")
    except Exception as e:
        logger.error(f"Error sending welcome message to user {user.id}: {str(e)}", exc_info=True)

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle the /help command"""
    user = update.effective_user
    logger.info(f"Help command ontvangen van user {user.id} ({user.first_name})")
    
    try:
        await update.message.reply_text(
            "🤖 TradingBot Help:\n\n"
            "Commando's:\n"
            "/start - Start de bot\n"
            "/help - Toon dit help bericht\n"
            "/status - Check bot status"
        )
        logger.debug(f"Help bericht verzonden naar user {user.id}")
    except Exception as e:
        logger.error(f"Fout bij verzenden help bericht naar user {user.id}: {str(e)}")

async def status_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle the /status command"""
    user = update.effective_user
    logger.info(f"Status command ontvangen van user {user.id} ({user.first_name})")
    
    try:
        await update.message.reply_text("✅ Bot is online en actief!")
        logger.debug(f"Status bericht verzonden naar user {user.id}")
    except Exception as e:
        logger.error(f"Fout bij verzenden status bericht naar user {user.id}: {str(e)}")

async def echo_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Echo all non-command messages and log them"""
    logger.debug("Echo handler aangeroepen")
    if update.message:
        user = update.effective_user
        text = update.message.text
        logger.info(f"Received message from {user.id} ({user.first_name}): {text}")
        try:
            message = await update.message.reply_text(f"Je stuurde: {text}")
            logger.debug(f"Echo bericht verzonden: {message.message_id}")
        except Exception as e:
            logger.error(f"Fout bij echo bericht: {str(e)}", exc_info=True)

async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle button callbacks"""
    query = update.callback_query
    await query.answer()
    
    try:
        if query.data.startswith("market_"):
            # Show instruments for selected market
            market_id = query.data.replace("market_", "")
            market_data = MARKETS[market_id]
            
            keyboard = [
                [InlineKeyboardButton(instrument, callback_data=f"instrument_{market_id}_{instrument}")]
                for instrument in market_data["instruments"]
            ]
            keyboard.append([InlineKeyboardButton("🔙 Back to Markets", callback_data="back_to_markets")])
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await query.message.edit_text(
                f"Select a {market_data['name']} instrument:",
                reply_markup=reply_markup
            )
        
        elif query.data.startswith("instrument_"):
            # Show timeframe selection
            _, market_id, instrument = query.data.split("_", 2)
            
            keyboard = [
                [InlineKeyboardButton(tf, callback_data=f"timeframe_{market_id}_{instrument}_{tf}")]
                for tf in TIMEFRAMES
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
            user_id = query.from_user.id
            
            try:
                # Save to Supabase
                data = {
                    "user_id": user_id,
                    "market": market_id,
                    "instrument": instrument,
                    "timeframe": timeframe
                }
                
                # Check for duplicates
                response = supabase.table("signal_preferences").select("*").eq(
                    "user_id", user_id
                ).eq("market", market_id).eq("instrument", instrument).eq(
                    "timeframe", timeframe
                ).execute()
                
                if not response.data:  # No duplicate found
                    result = supabase.table("signal_preferences").insert(data).execute()
                    logger.info(f"Saved preference to Supabase: {data}")
                    
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
                    await query.message.edit_text(
                        "⚠️ This preference already exists!\n"
                        "Please choose a different combination.",
                        reply_markup=InlineKeyboardMarkup([[
                            InlineKeyboardButton("🔙 Back to Markets", callback_data="back_to_markets")
                        ]])
                    )
                    
            except Exception as e:
                logger.error(f"Error saving preference: {str(e)}", exc_info=True)
                await query.message.edit_text(
                    "❌ Error saving your preference. Please try again."
                )
        
        elif query.data == "back_to_markets":
            # Show market selection
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
            user_id = query.from_user.id
            try:
                response = supabase.table("signal_preferences").select("*").eq(
                    "user_id", user_id
                ).execute()
                preferences = response.data

                if preferences:
                    text = "📋 Your signal preferences:\n\n"
                    for i, pref in enumerate(preferences, 1):
                        text += f"{i}. {pref['market'].upper()} - {pref['instrument']} ({pref['timeframe']})\n"
                    
                    # Maak delete knoppen voor elke voorkeur
                    keyboard = []
                    for i, pref in enumerate(preferences, 1):
                        keyboard.append([
                            InlineKeyboardButton(
                                f"🗑️ Delete #{i}: {pref['instrument']} ({pref['timeframe']})", 
                                callback_data=f"delete_preference_{pref['id']}"
                            )
                        ])
                    
                    keyboard.append([
                        InlineKeyboardButton("➕ Add More", callback_data="back_to_markets"),
                        InlineKeyboardButton("🔙 Back", callback_data="back_to_markets")
                    ])
                    reply_markup = InlineKeyboardMarkup(keyboard)
                    
                    await query.message.edit_text(text, reply_markup=reply_markup)
                else:
                    keyboard = [
                        [InlineKeyboardButton("➕ Add Preferences", callback_data="back_to_markets")]
                    ]
                    reply_markup = InlineKeyboardMarkup(keyboard)
                    
                    await query.message.edit_text(
                        "You don't have any signal preferences yet.",
                        reply_markup=reply_markup
                    )
            except Exception as e:
                logger.error(f"Error fetching preferences: {str(e)}", exc_info=True)
                await query.message.edit_text(
                    "❌ Error loading your preferences. Please try again."
                )

        elif query.data.startswith("delete_preference_"):
            user_id = query.from_user.id
            preference_id = int(query.data.replace("delete_preference_", ""))
            
            try:
                # Haal eerst de voorkeur op die verwijderd gaat worden
                pref_response = supabase.table("signal_preferences").select("*").eq(
                    "id", preference_id
                ).execute()
                
                if pref_response.data:
                    pref = pref_response.data[0]
                    # Verwijder de specifieke voorkeur
                    response = supabase.table("signal_preferences").delete().eq(
                        "id", preference_id
                    ).execute()
                    
                    # Toon bevestiging en opties
                    text = f"✅ Deleted preference:\n{pref['market'].upper()} - {pref['instrument']} ({pref['timeframe']})"
                    
                    keyboard = [
                        [
                            InlineKeyboardButton("📋 View Remaining", callback_data="view_preferences"),
                            InlineKeyboardButton("➕ Add New", callback_data="back_to_markets")
                        ]
                    ]
                    reply_markup = InlineKeyboardMarkup(keyboard)
                    
                    await query.message.edit_text(text, reply_markup=reply_markup)
                else:
                    await query.message.edit_text(
                        "❌ Preference not found. It might have been already deleted.",
                        reply_markup=InlineKeyboardMarkup([[
                            InlineKeyboardButton("📋 View Preferences", callback_data="view_preferences")
                        ]])
                    )
                    
            except Exception as e:
                logger.error(f"Error deleting preference: {str(e)}", exc_info=True)
                await query.message.edit_text(
                    "❌ Error deleting preference. Please try again."
                )
        
        elif query.data.startswith("analysis_"):
            instrument = query.data.replace("analysis_", "")
            try:
                # Get cached chart
                chart_bytes = redis_client.get(f"chart:{instrument}")
                if not chart_bytes:
                    raise Exception("Chart not found in cache")
                
                await query.message.delete()
                await context.bot.send_photo(
                    chat_id=query.message.chat_id,
                    photo=chart_bytes,
                    caption=f"📊 <b>Technical Analysis for {instrument}</b>",
                    parse_mode='HTML',
                    reply_markup=InlineKeyboardMarkup([
                        [InlineKeyboardButton("🔄 Update Analysis", callback_data=f"analysis_{instrument}")],
                        [InlineKeyboardButton("🔙 Back to Signal", callback_data=f"back_to_signal_{instrument}")]
                    ])
                )
                
            except Exception as e:
                logger.error(f"Error generating chart: {str(e)}", exc_info=True)
                await query.message.edit_text(
                    "❌ <b>Error generating chart. Please try again.</b>",
                    parse_mode='HTML'
                )
                
        elif query.data.startswith("back_to_signal_"):
            instrument = query.data.replace("back_to_signal_", "")
            
            # Get original message from Redis
            message = redis_client.get(f"signal:{instrument}")
            if message:
                message = message.decode('utf-8')
                
                # Verwijder het huidige bericht
                await query.message.delete()
                
                # Stuur een nieuw bericht met de originele knoppen
                await context.bot.send_message(
                    chat_id=query.message.chat_id,
                    text=message,
                    parse_mode='HTML',
                    reply_markup=InlineKeyboardMarkup([
                        [
                            InlineKeyboardButton("📊 Technical Analysis", callback_data=f"analysis_{instrument}"),
                            InlineKeyboardButton("📰 Market Sentiment", callback_data=f"sentiment_{instrument}")
                        ],
                        [
                            InlineKeyboardButton("📅 Economic Calendar", callback_data=f"calendar_{instrument}")
                        ]
                    ])
                )
            else:
                await query.message.edit_text(
                    text="❌ <b>Signal expired. Please wait for a new signal.</b>",
                    parse_mode='HTML',
                    reply_markup=InlineKeyboardMarkup([[
                        InlineKeyboardButton("🔙 Back", callback_data="back_to_markets")
                    ]])
                )
        
        elif query.data.startswith("sentiment_"):
            instrument = query.data.replace("sentiment_", "")
            try:
                # Get cached sentiment
                sentiment = redis_client.get(f"sentiment:{instrument}")
                
                if sentiment:
                    sentiment_text = sentiment.decode('utf-8')
                else:
                    # Fallback to new analysis if cache missed
                    sentiment_text = await sentiment_analyzer.analyze(instrument)
                
                # Get current message text
                current_text = query.message.text
                
                # Only update if content is different
                if current_text != sentiment_text:
                    await query.message.edit_text(
                        text=sentiment_text,
                        parse_mode='HTML',
                        reply_markup=InlineKeyboardMarkup([
                            [InlineKeyboardButton("🔄 Update Sentiment", callback_data=f"sentiment_{instrument}")],
                            [InlineKeyboardButton("🔙 Back to Signal", callback_data=f"back_to_signal_{instrument}")]
                        ])
                    )
                else:
                    # Just acknowledge the callback
                    await query.answer("Sentiment is already up to date!")
                    
            except Exception as e:
                logger.error(f"Error getting sentiment: {str(e)}")
                if "Message is not modified" not in str(e):  # Ignore this specific error
                    await query.message.edit_text(
                        "❌ <b>Error getting market sentiment. Please try again.</b>",
                        parse_mode='HTML',
                        reply_markup=InlineKeyboardMarkup([[
                            InlineKeyboardButton("🔙 Back to Signal", callback_data=f"back_to_signal_{instrument}")
                        ]])
                    )
        
        elif query.data.startswith("calendar_"):
            instrument = query.data.replace("calendar_", "")
            try:
                # Get cached calendar
                calendar = redis_client.get(f"calendar:{instrument}")
                
                if calendar:
                    calendar_text = calendar.decode('utf-8')
                else:
                    # Fallback to new analysis if cache missed
                    calendar_text = await economic_calendar.get_events()
                
                await query.message.edit_text(
                    text=calendar_text,
                    parse_mode='HTML',
                    reply_markup=InlineKeyboardMarkup([
                        [InlineKeyboardButton("🔄 Update Calendar", callback_data=f"calendar_{instrument}")],
                        [InlineKeyboardButton("🔙 Back to Signal", callback_data=f"back_to_signal_{instrument}")]
                    ])
                )
                    
            except Exception as e:
                logger.error(f"Error getting calendar: {str(e)}")
                await query.message.edit_text(
                    "❌ <b>Error getting economic calendar. Please try again.</b>",
                    parse_mode='HTML',
                    reply_markup=InlineKeyboardMarkup([[
                        InlineKeyboardButton("🔙 Back to Signal", callback_data=f"back_to_signal_{instrument}")
                    ]])
                )
        
    except Exception as e:
        logger.error(f"Error in button callback: {str(e)}", exc_info=True)
        await query.message.reply_text("An error occurred. Please try again.")

async def view_preferences(user_id: int):
    """Fetch user preferences from Supabase"""
    try:
        response = supabase.table("signal_preferences").select("*").eq(
            "user_id", user_id
        ).execute()
        
        return response.data
    except Exception as e:
        logger.error(f"Error fetching preferences: {str(e)}", exc_info=True)
        return None

def register_handlers(app):
    """Register all bot handlers"""
    logger.info("Registering bot handlers...")
    try:
        # Error handler
        app.add_error_handler(error_handler)
        
        # Command handlers
        app.add_handler(CommandHandler("start", start_command))
        app.add_handler(CommandHandler("help", help_command))
        app.add_handler(CommandHandler("status", status_command))
        
        # Callback handler voor inline knoppen
        app.add_handler(CallbackQueryHandler(button_callback))
        
        # Message handler for all other messages
        app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo_message))
        
        logger.info("Bot handlers successfully registered")
    except Exception as e:
        logger.error(f"Fout bij registreren van handlers: {str(e)}", exc_info=True)

# Na de andere initialisaties
chart_analyzer = ChartAnalyzer()
economic_calendar = EconomicCalendar() 