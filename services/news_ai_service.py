from openai import OpenAI
import logging
import os

logger = logging.getLogger(__name__)

class NewsAIService:
    def __init__(self, db):
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.db = db
        
    async def analyze_sentiment(self, symbol: str) -> str:
        """Analyze market sentiment with caching"""
        try:
            # Check cache
            cached = await self.db.get_cached_sentiment(symbol)
            if cached:
                return cached
                
            # Get fresh analysis
            sentiment = await self._get_openai_analysis(symbol)
            
            # Cache result
            await self.db.cache_sentiment(symbol, sentiment)
            
            return sentiment
            
        except Exception as e:
            logger.error(f"Error analyzing sentiment: {str(e)}")
            return "Sentiment analysis unavailable"
            
    async def _get_openai_analysis(self, symbol: str) -> str:
        """Get sentiment analysis from OpenAI"""
        try:
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a market analyst providing brief sentiment analysis."},
                    {"role": "user", "content": f"Analyze current market sentiment for {symbol} briefly"}
                ],
                max_tokens=200
            )
            return response.choices[0].message.content
        except Exception as e:
            logger.error(f"OpenAI API error: {str(e)}")
            return "Error getting sentiment analysis"
