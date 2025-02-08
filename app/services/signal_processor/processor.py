from app.services.signal_processor.models import TradingSignal, SignalType
from app.utils.logger import logger
from app.utils.supabase import supabase
from app.services.subscriber.matcher import SubscriberMatcher
from app.services.telegram.notifier import TelegramNotifier
from app.services.sentiment.analyzer import SentimentAnalyzer
from app.services.chart.analyzer import ChartAnalyzer
from app.services.calendar.analyzer import EconomicCalendar
from app.utils.redis import redis_client
from telegram import InlineKeyboardMarkup, InlineKeyboardButton

class SignalProcessor:
    def __init__(self):
        self.logger = logger
        self.subscriber_matcher = SubscriberMatcher()
        self.telegram_bot = TelegramNotifier()
        self.sentiment_analyzer = SentimentAnalyzer()
        self.chart_analyzer = ChartAnalyzer()
        self.economic_calendar = EconomicCalendar()
        self.redis_client = redis_client

    async def process_tradingview_webhook(self, data: dict) -> None:
        """Process incoming webhook from TradingView"""
        try:
            logger.info("🔄 Starting signal processing...")
            
            # 1. Create signal object
            signal = TradingSignal(**data)
            logger.info(f"✅ Signal object created for {signal.symbol}")
            
            # 2. Get subscribers first
            logger.info("👥 Finding matching subscribers...")
            subscribers = await self._get_matching_subscribers(signal)
            logger.info(f"✅ Found {len(subscribers)} subscribers")
            
            # 3. Load ALL data
            logger.info("📥 Loading all required data...")
            
            # Get sentiment analysis
            logger.info("🔍 Getting market sentiment...")
            sentiment = await self.sentiment_analyzer.analyze(signal.symbol)
            logger.info("✅ Sentiment analysis complete")
            
            # Generate technical analysis chart
            logger.info("📊 Generating technical analysis...")
            chart_bytes = await self.chart_analyzer.generate_chart(signal.symbol)
            logger.info("✅ Chart generation complete")
            
            # Get calendar data
            logger.info("📅 Loading economic calendar...")
            calendar_data = await self.economic_calendar.get_events()
            logger.info("✅ Calendar data loaded")
            
            # Format messages
            logger.info("📝 Formatting messages...")
            signal_message = self._format_signal_message(signal, sentiment)
            
            # 4. Store everything in Redis
            logger.info("💾 Caching all data...")
            self.redis_client.set(f"signal:{signal.symbol}", signal_message, ex=3600)
            self.redis_client.set(f"sentiment:{signal.symbol}", sentiment, ex=3600)
            self.redis_client.set(f"chart:{signal.symbol}", chart_bytes, ex=3600)
            self.redis_client.set(
                f"calendar:{signal.symbol}",
                calendar_data,
                ex=3600
            )
            logger.info("✅ All data cached")
            
            # 5. Send to subscribers
            logger.info("📤 Starting message dispatch...")
            for subscriber in subscribers:
                try:
                    logger.info(f"Sending to subscriber {subscriber['chat_id']}...")
                    await self.telegram_bot.send_message(
                        chat_id=subscriber['chat_id'],
                        text=signal_message,
                        parse_mode='HTML',
                        reply_markup=InlineKeyboardMarkup([
                            [
                                InlineKeyboardButton("📊 Technical Analysis", callback_data=f"analysis_{signal.symbol}"),
                                InlineKeyboardButton("📰 Market Sentiment", callback_data=f"sentiment_{signal.symbol}")
                            ],
                            [
                                InlineKeyboardButton("📅 Economic Calendar", callback_data=f"calendar_{signal.symbol}")
                            ]
                        ])
                    )
                    logger.info(f"✅ Message sent to {subscriber['chat_id']}")
                except Exception as e:
                    logger.error(f"❌ Error sending to {subscriber['chat_id']}: {str(e)}")
                    logger.exception(e)
            
            logger.info("✅ Signal processing complete!")
            return signal
            
        except Exception as e:
            logger.error(f"❌ Error processing webhook: {str(e)}")
            logger.exception(e)
            raise

    async def _save_signal(self, signal: TradingSignal):
        """Save signal to database"""
        try:
            # Convert to dict and handle datetime manually
            data = signal.dict(exclude={'id'})  # Exclude id field
            data['created_at'] = data['created_at'].isoformat()
            
            result = supabase.table("trading_signals").insert(data).execute()
            self.logger.info(f"Signal saved to database: {signal.symbol}")
            return result
        except Exception as e:
            self.logger.error(f"Error saving signal to database: {str(e)}", exc_info=True)
            raise

    async def _get_matching_subscribers(self, signal: TradingSignal):
        """Get matching subscribers for the signal"""
        try:
            return await self.subscriber_matcher.find_matching_subscribers(signal)
        except Exception as e:
            self.logger.error(f"Error getting matching subscribers: {str(e)}")
            raise

    def _format_signal_message(self, signal: TradingSignal, sentiment: str = None) -> str:
        """Format signal message with sentiment"""
        message = f"""Signal for {signal.symbol}

Instrument: {signal.symbol}
Action: {signal.action} {'📈' if signal.action == 'BUY' else '📉'}

Entry Price: {signal.price}
Stop Loss: {signal.stop_loss} 🔴
Take Profit: {signal.take_profit} 🎯

Timeframe: {signal.timeframe}
Strategy: {signal.strategy}

------------------

Risk Management:
• Position size: 1-2% max
• Use proper stop loss
• Follow your trading plan

------------------

🤖 SigmaPips AI Verdict:
✅ {self._get_ai_verdict(sentiment)}"""

        return message

    def _get_ai_verdict(self, sentiment: str) -> str:
        """Extract verdict from sentiment analysis"""
        try:
            if not sentiment:
                return "Trade aligns with market analysis"  # Default if no sentiment
                
            # Find Direction in sentiment
            direction_line = next(
                (line for line in sentiment.split('\n') 
                if 'Direction:' in line),
                None
            )
            
            if not direction_line:
                return "Trade aligns with market analysis"  # Default if no direction found
                
            direction = direction_line.split('Direction:')[1].strip()
            
            # Determine if trade aligns with sentiment
            if direction.lower() in ['bullish', 'bearish']:
                return "Trade aligns with market analysis"
            else:
                return "Mixed market signals - trade with caution"
                
        except Exception as e:
            logger.error(f"Error getting AI verdict: {str(e)}")
            return "Trade aligns with market analysis"  # Default fallback

    def get_signal(self, instrument: str) -> str:
        """Get signal from Redis"""
        try:
            signal = self.redis_client.get(f"signal:{instrument}")
            if signal:
                return signal.decode('utf-8')
            return None
        except Exception as e:
            self.logger.error(f"Error getting signal from Redis: {str(e)}")
            return None
