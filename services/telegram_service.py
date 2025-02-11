import aiohttp
import logging
from typing import Dict, Any
import os
from services.database import Database

logger = logging.getLogger(__name__)

class TelegramService:
    def __init__(self, token: str, db: Database):
        self.token = token
        self.db = db
        
    async def send_signal(self, chat_id: str, signal: Dict[str, Any], sentiment: str, 
                         chart: bytes, events: list, **kwargs):
        """Send complete signal message to subscriber"""
        try:
            # Convert 'type' to 'action' if needed
            signal['action'] = signal.get('type', signal.get('action', 'UNKNOWN'))
            
            # Format message
            message = await self._format_signal_message(signal, sentiment, events)
            
            # Send message and chart
            async with aiohttp.ClientSession() as session:
                # Send text message
                await self._send_message(session, chat_id, message)
                
                # Send chart if available
                if chart:
                    await self._send_photo(session, chat_id, chart)
                    
        except Exception as e:
            logger.error(f"Error sending signal to {chat_id}: {str(e)}")
            raise 

    async def _format_signal_message(self, signal: Dict, sentiment: str, events: list) -> str:
        """Format signal message with sentiment and events"""
        return f"""
🔔 *TRADING SIGNAL*
Symbol: {signal['symbol']}
Action: {signal['action']}
Price: {signal['price']}
Stop Loss: {signal['stopLoss']}
Take Profit: {signal['takeProfit']}

📊 *SENTIMENT*
{sentiment}

📅 *RELEVANT EVENTS*
{self._format_events(events)}
"""

    async def _send_message(self, session, chat_id: str, message: str):
        """Send message via Telegram"""
        url = f"https://api.telegram.org/bot{self.token}/sendMessage"
        await session.post(url, json={
            "chat_id": chat_id,
            "text": message,
            "parse_mode": "Markdown"
        })

    async def _send_photo(self, session, chat_id: str, photo: bytes):
        """Send photo via Telegram"""
        url = f"https://api.telegram.org/bot{self.token}/sendPhoto"
        form = aiohttp.FormData()
        form.add_field("chat_id", chat_id)
        form.add_field("photo", photo, filename="chart.png")
        await session.post(url, data=form) 

    def _format_events(self, events: list) -> str:
        """Format calendar events for message"""
        if not events:
            return "No relevant events"
        return "\n".join([f"• {event}" for event in events]) 

    async def send_welcome_message(self, chat_id: str):
        """Send welcome message to new users"""
        welcome_message = """
🤖 *Welcome to SigmaPips Trading Bot!*

I will help you set up your trading preferences.
Please answer a few questions to get started.
"""
        
        # Keyboard voor markten (verticaal, zonder emoji's)
        keyboard = {
            "inline_keyboard": [
                [{"text": "Forex", "callback_data": "market_forex"}],
                [{"text": "Indices", "callback_data": "market_indices"}],
                [{"text": "Commodities", "callback_data": "market_commodities"}],
                [{"text": "Crypto", "callback_data": "market_crypto"}]
            ]
        }
        
        async with aiohttp.ClientSession() as session:
            await session.post(f"https://api.telegram.org/bot{self.token}/sendMessage", 
                json={
                    "chat_id": chat_id,
                    "text": welcome_message,
                    "parse_mode": "Markdown",
                    "reply_markup": keyboard
                })

    async def handle_telegram_command(self, message: Dict[str, Any]):
        """Handle Telegram commands"""
        command = message['text']
        chat_id = message['chat']['id']
        
        if command == '/start':
            return await self.send_welcome_message(chat_id)
        elif command == '/preferences':
            return await self.show_preferences(chat_id)
        
        return {"status": "unknown_command"}

    async def show_preferences(self, chat_id: str):
        """Show current preferences and management options"""
        # Haal huidige voorkeuren op uit database
        preferences = await self.db.get_subscriber_preferences(chat_id)
        
        message = """
🔧 *Your Trading Preferences*

Here are your current signal combinations:
"""
        
        # Voeg elke combinatie toe aan het bericht
        for pref in preferences:
            message += f"\n• {pref['market']} - {pref['instrument']} ({pref['timeframe']})"
        
        message += """

Actions:
• Add new combination: /start
• Remove combination: Use buttons below
• Clear all: /clear
"""

        # Maak keyboard met delete knoppen voor elke combinatie
        keyboard = {
            "inline_keyboard": [
                [{"text": f"🗑️ Delete {p['instrument']} ({p['timeframe']})", 
                  "callback_data": f"delete_pref_{p['id']}"} 
                ] for p in preferences
            ]
        }
        
        async with aiohttp.ClientSession() as session:
            await session.post(f"https://api.telegram.org/bot{self.token}/sendMessage",
                json={
                    "chat_id": chat_id,
                    "text": message,
                    "parse_mode": "Markdown",
                    "reply_markup": keyboard
                })

    async def handle_callback_query(self, callback_query: Dict[str, Any]):
        """Handle callback queries from inline keyboards"""
        try:
            data = callback_query['data']
            chat_id = callback_query['message']['chat']['id']
            
            if data.startswith('market_'):
                market = data.split('_')[1]
                await self.db.save_user_state(chat_id, {'market': market})
                await self._ask_instrument(chat_id, market)
                
            elif data.startswith('instrument_'):
                instrument = data.split('_')[1]
                state = await self.db.get_user_state(chat_id)
                state['instrument'] = instrument
                await self.db.save_user_state(chat_id, state)
                await self._ask_timeframe(chat_id, instrument)
                
            elif data.startswith('timeframe_'):
                timeframe = data.split('_')[1]
                state = await self.db.get_user_state(chat_id)
                preference = {
                    'market': state['market'],
                    'instrument': state['instrument'],
                    'timeframe': timeframe
                }
                await self.db.save_preference(chat_id, preference)
                await self.db.save_user_state(chat_id, {})
                await self._ask_add_more(chat_id)
                
            elif data == 'back_to_markets':
                await self.db.save_user_state(chat_id, {})
                await self.send_welcome_message(chat_id)
                
            elif data == 'back_to_instruments':
                state = await self.db.get_user_state(chat_id)
                await self._ask_instrument(chat_id, state['market'])
                
            # Answer callback query
            async with aiohttp.ClientSession() as session:
                await session.post(
                    f"https://api.telegram.org/bot{self.token}/answerCallbackQuery",
                    json={"callback_query_id": callback_query['id']}
                )
                
            return {"status": "callback_handled"}
            
        except Exception as e:
            logger.error(f"Error handling callback: {str(e)}")
            raise

    async def _ask_instrument(self, chat_id: str, market: str):
        """Ask user for specific instruments based on market"""
        instruments = {
            "forex": [
                [{"text": "EURUSD", "callback_data": "instrument_EURUSD"},
                 {"text": "GBPUSD", "callback_data": "instrument_GBPUSD"}],
                [{"text": "USDJPY", "callback_data": "instrument_USDJPY"},
                 {"text": "USDCHF", "callback_data": "instrument_USDCHF"}],
                [{"text": "AUDUSD", "callback_data": "instrument_AUDUSD"}],
                [{"text": "⬅️ Back", "callback_data": "back_to_markets"}]  # Back knop
            ],
            "indices": [
                [{"text": "S&P 500", "callback_data": "instrument_SP500"},
                 {"text": "NASDAQ 100", "callback_data": "instrument_NAS100"}],
                [{"text": "Dow Jones", "callback_data": "instrument_DJI"},
                 {"text": "DAX 40", "callback_data": "instrument_DAX40"}],
                [{"text": "FTSE 100", "callback_data": "instrument_FTSE100"}],
                [{"text": "⬅️ Back", "callback_data": "back_to_markets"}]  # Back knop
            ],
            "commodities": [
                [{"text": "Gold (XAUUSD)", "callback_data": "instrument_XAUUSD"},
                 {"text": "Silver (XAGUSD)", "callback_data": "instrument_XAGUSD"}],
                [{"text": "Oil (WTI)", "callback_data": "instrument_WTI"},
                 {"text": "Oil (Brent)", "callback_data": "instrument_Brent"}],
                [{"text": "Natural Gas", "callback_data": "instrument_NGAS"}]
            ],
            "crypto": [
                [{"text": "Bitcoin (BTCUSD)", "callback_data": "instrument_BTCUSD"},
                 {"text": "Ethereum (ETHUSD)", "callback_data": "instrument_ETHUSD"}],
                [{"text": "Ripple (XRPUSD)", "callback_data": "instrument_XRPUSD"},
                 {"text": "Solana (SOLUSD)", "callback_data": "instrument_SOLUSD"}],
                [{"text": "Litecoin (LTCUSD)", "callback_data": "instrument_LTCUSD"}]
            ]
        }
        
        keyboard = {
            "inline_keyboard": instruments[market.lower()]
        }
        
        message = f"Great! You selected {market}.\nNow choose your instrument:"
        
        async with aiohttp.ClientSession() as session:
            await session.post(f"https://api.telegram.org/bot{self.token}/sendMessage",
                json={
                    "chat_id": chat_id,
                    "text": message,
                    "reply_markup": keyboard
                })

    async def _ask_timeframe(self, chat_id: str, instrument: str):
        """Ask user for preferred timeframe"""
        keyboard = {
            "inline_keyboard": [
                [
                    {"text": "15m", "callback_data": "timeframe_15m"},
                    {"text": "1h", "callback_data": "timeframe_1h"},
                    {"text": "4h", "callback_data": "timeframe_4h"}
                ],
                [{"text": "⬅️ Back", "callback_data": "back_to_instruments"}]  # Back knop
            ]
        }
        
        message = f"Excellent! You selected {instrument}.\nLastly, choose your timeframe:"
        
        async with aiohttp.ClientSession() as session:
            await session.post(f"https://api.telegram.org/bot{self.token}/sendMessage",
                json={
                    "chat_id": chat_id,
                    "text": message,
                    "reply_markup": keyboard
                }) 

    async def _save_preference(self, chat_id: str, timeframe: str):
        """Save user preference"""
        # Implementeer de logica om de voorkeur op te slaan in de database
        pass

    async def _delete_preference(self, chat_id: str, pref_id: str):
        """Delete user preference"""
        # Implementeer de logica om de voorkeur te verwijderen uit de database
        pass

    async def _ask_add_more(self, chat_id: str):
        """Vraag of gebruiker nog een combinatie wil toevoegen"""
        message = "Preference saved! Would you like to add another combination?"
        
        keyboard = {
            "inline_keyboard": [
                [
                    {"text": "✅ Yes", "callback_data": "add_more_yes"},
                    {"text": "❌ No", "callback_data": "add_more_no"}
                ]
            ]
        }
        
        async with aiohttp.ClientSession() as session:
            await session.post(f"https://api.telegram.org/bot{self.token}/sendMessage",
                json={
                    "chat_id": chat_id,
                    "text": message,
                    "reply_markup": keyboard
                }) 
