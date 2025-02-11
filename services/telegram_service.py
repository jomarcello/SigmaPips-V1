import aiohttp
import logging
from typing import Dict, Any
import os

logger = logging.getLogger(__name__)

class TelegramService:
    def __init__(self, db):
        self.token = os.getenv("TELEGRAM_BOT_TOKEN")
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
