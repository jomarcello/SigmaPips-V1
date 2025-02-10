import logging
from typing import Dict, Any
from app.services.technical_analysis import analyze_technical
from app.services.news_sentiment import analyze_sentiment
from app.services.chart_analysis import generate_chart_analysis

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
        return {
            "status": "distributed",
            "signal": signal
        }
    except Exception as e:
        logger.error(f"Signal distribution error: {str(e)}")
        raise 