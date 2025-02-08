from supabase import create_client
import redis
import logging
import os
from typing import Dict, List
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

logger = logging.getLogger(__name__)

class Database:
    def __init__(self):
        # Initialize connections
        supabase_url = os.getenv("SUPABASE_URL")
        supabase_key = os.getenv("SUPABASE_KEY")
        
        if not supabase_url or not supabase_key:
            logger.error("Missing Supabase credentials in .env file")
            raise ValueError("SUPABASE_URL and SUPABASE_KEY are required")
            
        self.supabase = create_client(supabase_url, supabase_key)
        self.redis = redis.Redis(
            host=os.getenv("REDIS_HOST", "localhost"),
            port=int(os.getenv("REDIS_PORT", 6379)),
            decode_responses=True
        )
        
        self.CACHE_TIMEOUT = 300  # 5 minuten in seconden
        
    async def match_subscribers(self, signal: Dict) -> List[Dict]:
        """Match signal with subscriber preferences"""
        try:
            logger.info(f"Attempting to connect to Supabase with URL: {self.supabase.supabase_url}")
            logger.info(f"Incoming signal: {signal}")
            
            response = self.supabase.table("subscribers").select("*").execute()
            logger.info(f"Supabase response: {response}")
            
            # Transform subscriber data to include chat_id
            subscribers = []
            for s in response.data:
                s['chat_id'] = str(s['user_id'])  # Use user_id as chat_id
                subscribers.append(s)
            
            matches = [s for s in subscribers if self._matches_preferences(signal, s)]
            logger.info(f"Matched subscribers: {matches}")
            return matches
        
        except Exception as e:
            logger.error(f"Error matching subscribers: {str(e)}", exc_info=True)
            return []

    def _matches_preferences(self, signal: Dict, subscriber: Dict) -> bool:
        """Check if signal matches subscriber preferences"""
        logger.info(f"Checking preferences for subscriber: {subscriber}")
        
        # Check symbol
        if subscriber.get("symbols"):
            logger.info(f"Subscriber symbols: {subscriber['symbols']}, Signal symbol: {signal['symbol']}")
            if signal["symbol"] not in subscriber["symbols"]:
                logger.info("Symbol mismatch")
                return False
        
        # Check timeframe
        if subscriber.get("timeframes"):
            logger.info(f"Subscriber timeframes: {subscriber['timeframes']}, Signal interval: {signal['interval']}")
            if signal["interval"] not in subscriber["timeframes"]:
                logger.info("Timeframe mismatch")
                return False
        
        logger.info("Subscriber matches all preferences")
        return True

    async def get_cached_sentiment(self, symbol: str) -> str:
        """Get cached sentiment analysis"""
        return self.redis.get(f"sentiment:{symbol}")

    async def cache_sentiment(self, symbol: str, sentiment: str) -> None:
        """Cache sentiment analysis"""
        try:
            # Gebruik de class constant voor timeout
            await self.redis.set(f"sentiment:{symbol}", sentiment, ex=self.CACHE_TIMEOUT)
        except Exception as e:
            logger.error(f"Error caching sentiment: {str(e)}")

    async def cache_sentiment_old(self, symbol: str, sentiment: str):
        """Cache sentiment analysis"""
        self.redis.setex(
            f"sentiment:{symbol}",
            int(os.getenv("CACHE_DURATION", 300)),
            sentiment
        ) 