import logging
from typing import Dict, Any
from app.utils.supabase import supabase
from app.services.telegram.service import TelegramService
from app.services.sentiment.service import NewsAIService
from app.services.chart.service import ChartService
from app.services.calendar.service import CalendarService

logger = logging.getLogger(__name__)

class SignalProcessor:
    def __init__(self):
        self.telegram_service = TelegramService(supabase)
        self.news_service = NewsAIService(supabase)
        self.chart_service = ChartService()
        self.calendar_service = CalendarService(supabase)

    async def process_signal(self, signal_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process incoming signal through all services"""
        try:
            # Get analyses from all services
            sentiment = await self.news_service.analyze_sentiment(signal_data["instrument"])
            chart = await self.chart_service.generate_chart(
                signal_data["instrument"], 
                signal_data["timeframe"]
            )
            events = await self.calendar_service.get_relevant_events(signal_data["instrument"])

            # Combine all analyses
            complete_signal = {
                **signal_data,
                "sentiment_analysis": sentiment,
                "chart": chart,
                "calendar_events": events
            }

            logger.info(f"Signal processed successfully: {complete_signal}")
            return complete_signal

        except Exception as e:
            logger.error(f"Signal processing error: {str(e)}")
            raise

    async def distribute_signal(self, signal: Dict[str, Any]) -> Dict[str, Any]:
        """Distribute signal to subscribers"""
        try:
            # Get subscribers
            response = supabase.table("signal_preferences").select("*").eq(
                "market", signal["market"]
            ).eq("instrument", signal["instrument"]).eq(
                "timeframe", signal["timeframe"]
            ).execute()

            # Send to each subscriber
            sent_count = 0
            for pref in response.data:
                await self.telegram_service.send_signal(
                    chat_id=pref["user_id"],
                    signal=signal,
                    sentiment=signal["sentiment_analysis"],
                    chart=signal["chart"],
                    events=signal["calendar_events"]
                )
                sent_count += 1

            return {
                "status": "distributed",
                "sent_to": sent_count,
                "signal": signal
            }

        except Exception as e:
            logger.error(f"Signal distribution error: {str(e)}")
            raise

# Create singleton instance
processor = SignalProcessor()
