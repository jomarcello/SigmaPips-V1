from telegram import Bot
from telegram.ext import Application
import logging
import os
import ssl
import asyncio
from typing import Dict, Any
from telegram.constants import ParseMode
from trading_bot.services.database.db import Database

logger = logging.getLogger(__name__)

class TelegramService:
    def __init__(self, db):
        self.db = db
        self.token = os.getenv("TELEGRAM_BOT_TOKEN")
        
        if not self.token:
            raise ValueError("TELEGRAM_BOT_TOKEN not found in environment")
            
        # SSL setup zonder verificatie voor ontwikkeling
        ssl_context = ssl.create_default_context()
        ssl_context.check_hostname = False
        ssl_context.verify_mode = ssl.CERT_NONE
        
        request = Request(
            con_pool_size=8,
            connect_timeout=30.0,
            read_timeout=30.0,
            ssl_context=ssl_context,
            connection_pool_size=8
        )
        
        self.bot = telegram.Bot(token=self.token, request=request)
        
        # Test verbinding direct
        try:
            info = asyncio.run(self.bot.get_me())
            logger.info(f"Successfully connected to Telegram API. Bot info: {info}")
        except Exception as e:
            logger.error(f"Failed to connect to Telegram API: {str(e)}")
            raise
            
    async def send_signal(self, chat_id: str, signal: Dict[str, Any], sentiment: str = None, chart: str = None, events: list = None):
        try:
            message = self._format_signal_message(signal, sentiment, events)
            
            # Log de verzendpoging
            logger.info(f"Attempting to send message to chat_id: {chat_id}")
            logger.debug(f"Message content: {message}")
            
            await self.bot.send_message(
                chat_id=chat_id, 
                text=message, 
                parse_mode=ParseMode.HTML
            )
            
            if chart:
                await self.bot.send_photo(chat_id=chat_id, photo=chart)
                
            logger.info(f"Successfully sent message to chat_id: {chat_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send message to {chat_id}: {str(e)}", exc_info=True)
            return False
            
    def _format_signal_message(self, signal: Dict[str, Any], sentiment: str = None, events: list = None) -> str:
        """Format signal data into a readable message"""
        message = f"🚨 <b>New Signal Alert</b>\n\n"
        message += f"Symbol: {signal['symbol']}\n"
        message += f"Action: {signal['action']}\n"
        message += f"Price: {signal['price']}\n"
        message += f"Stop Loss: {signal['stopLoss']}\n"
        message += f"Take Profit: {signal['takeProfit']}\n"
        message += f"Timeframe: {signal.get('timeframe', 'Not specified')}\n"
        
        if sentiment:
            message += f"\n📊 <b>Sentiment Analysis</b>\n{sentiment}\n"
            
        if events and len(events) > 0:
            message += f"\n📅 <b>Upcoming Events</b>\n"
            for event in events[:3]:  # Show max 3 events
                message += f"• {event}\n"
                
        return message 