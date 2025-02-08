from app.services.signal_processor.models import TradingSignal
from app.utils.logger import logger
from telegram import Bot, Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackContext
import os
import logging

logger = logging.getLogger(__name__)

class TelegramNotifier:
    def __init__(self):
        self.token = os.getenv("TELEGRAM_BOT_TOKEN")
        logger.debug(f"Initializing TelegramNotifier with token: {self.token[:8]}...{self.token[-4:]}")
        self.bot = Bot(token=self.token)

    async def send_signal(self, signal: TradingSignal, user_ids: list[int], formatted_message: str):
        """Send trading signal to specified users"""
        try:
            keyboard = [
                [
                    InlineKeyboardButton("📊 Technical Analysis", callback_data=f"analysis_{signal.instrument}"),
                    InlineKeyboardButton("📰 Market Sentiment", callback_data=f"sentiment_{signal.instrument}")
                ]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            # Send to each user as pure text
            for user_id in user_ids:
                try:
                    await self.send_message(
                        chat_id=user_id,
                        text=formatted_message,
                        parse_mode='HTML',
                        reply_markup=reply_markup
                    )
                    logger.info(f"Signal sent to user {user_id}")
                except Exception as e:
                    logger.error(f"Failed to send signal to user {user_id}: {str(e)}")
                    continue
                    
        except Exception as e:
            logger.error(f"Error in send_signal: {str(e)}", exc_info=True)
            raise

    async def send_message(self, chat_id: int, text: str, parse_mode: str = None, reply_markup=None):
        """Send message to Telegram chat"""
        try:
            logger.info(f"Attempting to send message to chat_id: {chat_id}")
            logger.debug(f"Message text: {text[:100]}...")  # First 100 chars
            logger.debug(f"Parse mode: {parse_mode}")
            logger.debug(f"Reply markup: {reply_markup}")
            
            response = await self.bot.send_message(
                chat_id=chat_id,
                text=text,
                parse_mode=parse_mode,
                reply_markup=reply_markup
            )
            
            logger.info(f"Message successfully sent to {chat_id}, message_id: {response.message_id}")
            return response
            
        except Exception as e:
            logger.error(f"Failed to send message to {chat_id}")
            logger.error(f"Error type: {type(e).__name__}")
            logger.error(f"Error message: {str(e)}")
            logger.error(f"Bot token used: {self.token[:8]}...{self.token[-4:]}")
            raise

    def _format_signal_message(self, signal: TradingSignal) -> str:
        """Format trading signal as HTML message"""
        return (
            f"🚨 <b>New Trading Signal</b> 🚨\n\n"
            f"Market: {signal.market.upper()}\n"
            f"Instrument: {signal.instrument}\n"
            f"Signal: {signal.signal_type.value}\n"
            f"💰 Entry Price: {signal.entry_price}\n"
            f"🛑 Stop Loss: {signal.stop_loss}\n"
            f"✅ Take Profit: {signal.take_profit}\n"
            f"Timeframe: {signal.timeframe}\n"
            f"Strategy: {signal.strategy_name}\n\n"
            f"------------------\n\n"
            f"⚠️ Risk Management ⚠️\n"
            f"• Position size: 1-2% max\n"
            f"• Use proper stop loss\n"
            f"• Follow your trading plan\n\n"
            f"------------------\n\n"
            f"🤖 SigmaPips AI Verdict:\n"
        )

    def _create_signal_keyboard(self, signal: TradingSignal) -> InlineKeyboardMarkup:
        """Create inline keyboard for signal message"""
        keyboard = [
            [
                InlineKeyboardButton("📊 Technical Analysis", callback_data=f"analysis_{signal.instrument}"),
                InlineKeyboardButton("📰 Market Sentiment", callback_data=f"sentiment_{signal.instrument}")
            ]
        ]
        return InlineKeyboardMarkup(keyboard) 