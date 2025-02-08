from supabase import create_client
import redis
import logging
import os
from typing import Dict, List

logger = logging.getLogger(__name__)

class Database:
    def __init__(self):
        # Initialize connections
        self.supabase = create_client(
            os.getenv("SUPABASE_URL"),
            os.getenv("SUPABASE_KEY")
        )
        self.redis = redis.Redis(
            host=os.getenv("REDIS_HOST"),
            port=6379,
            decode_responses=True
        )
        
    async def match_subscribers(self, signal: Dict) -> List[Dict]:
        """Match signal with subscriber preferences"""
        try:
            response = self.supabase.table("subscribers").select("*").execute()
            return [s for s in response.data if self._matches_preferences(signal, s)]
        except Exception as e:
            logger.error(f"Error matching subscribers: {str(e)}")
            return [] 

    def _matches_preferences(self, signal: Dict, subscriber: Dict) -> bool:
        """Check if signal matches subscriber preferences"""
        # Check symbol
        if subscriber.get("symbols") and signal["symbol"] not in subscriber["symbols"]:
            return False
        
        # Check timeframe
        if subscriber.get("timeframes") and signal["interval"] not in subscriber["timeframes"]:
            return False
        
        return True

    async def get_cached_sentiment(self, symbol: str) -> str:
        """Get cached sentiment analysis"""
        return self.redis.get(f"sentiment:{symbol}")

    async def cache_sentiment(self, symbol: str, sentiment: str):
        """Cache sentiment analysis"""
        self.redis.setex(
            f"sentiment:{symbol}",
            int(os.getenv("CACHE_DURATION", 300)),
            sentiment
        ) 