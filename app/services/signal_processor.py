import logging
from typing import Dict, Any
from app.services.technical_analysis import analyze_technical
from app.services.news_sentiment import analyze_sentiment
from app.services.chart_analysis import generate_chart_analysis
from app.utils.supabase import supabase
from telegram import Bot
import os

# Initialize bot
bot = Bot(os.getenv("TELEGRAM_BOT_TOKEN"))

logger = logging.getLogger(__name__)

async def process_signal(signal_data: Dict[str, Any]) -> Dict[str, Any]:
    """Process incoming signal through all analysis services"""
    try:
        # Run all analyses in parallel
        technical = await analyze_technical(signal_data)
        sentiment = await analyze_sentiment(signal_data["instrument"])
        chart = await generate_chart_analysis(signal_data)
        
        # Combine all analyses
        complete_signal = {
            **signal_data,
            "technical_analysis": technical,
            "sentiment_analysis": sentiment,
            "chart_analysis": chart
        }
        
        logger.info(f"Signal processed successfully: {complete_signal}")
        return complete_signal
        
    except Exception as e:
        logger.error(f"Signal processing error: {str(e)}")
        raise

async def distribute_signal(signal: Dict[str, Any]) -> Dict[str, Any]:
    """Distribute signal to subscribers"""
    try:
        logger.info(f"Distributing signal: {signal}")
        
        # Get subscribers from database
        response = supabase.table("signal_preferences").select("*").eq(
            "market", signal["market"]
        ).eq("instrument", signal["instrument"]).eq(
            "timeframe", signal["timeframe"]
        ).execute()
        
        # Send to each subscriber
        sent_count = 0
        for pref in response.data:
            message = (
                f"🚨 SIGMAPIPS AI SIGNAL ALERT! 🚨\n\n"
                f"📊 {signal['instrument']} ({signal['timeframe']})\n"
                f"📈 Action: {signal['action']}\n"
                f"💰 Price: {signal['price']}\n\n"
                f"Technical Analysis:\n"
                f"• Trend: {signal['technical_analysis']['trend']}\n"
                f"• RSI: {signal['technical_analysis']['indicators']['rsi']}\n"
                f"• MACD: {signal['technical_analysis']['indicators']['macd']}\n\n"
                f"Sentiment: {signal['sentiment_analysis']['sentiment']}\n"
                f"Score: {signal['sentiment_analysis']['score']}\n\n"
                f"Chart Patterns: {', '.join(signal['chart_analysis']['patterns'])}\n"
                f"Support: {', '.join(signal['chart_analysis']['key_levels']['support'])}\n"
                f"Resistance: {', '.join(signal['chart_analysis']['key_levels']['resistance'])}"
            )
            
            await bot.send_message(
                chat_id=int(pref["user_id"]),
                text=message
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
