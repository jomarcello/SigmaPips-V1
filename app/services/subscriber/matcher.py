from app.services.signal_processor.models import TradingSignal
from app.utils.logger import logger
from app.utils.supabase import supabase
from typing import List

class SubscriberMatcher:
    def __init__(self):
        self.logger = logger

    async def find_matching_subscribers(self, signal: TradingSignal) -> list:
        """Find subscribers matching the signal criteria"""
        # Voor nu, stuur naar een test gebruiker
        return [{"chat_id": 2004519703}]  # Jouw chat_id

    async def find_matching_subscribers_from_database(self, signal: TradingSignal) -> list:
        """Find subscribers matching the signal criteria from the database"""
        try:
            # Query subscribers based on market and symbol
            response = supabase.table("signal_preferences").select(
                "signal_preferences.id",
                "signal_preferences.market",
                "signal_preferences.symbol",
                "signal_preferences.timeframe",
                "users.chat_id"  # Zorg dat we chat_id hebben
            ).eq(
                "market", signal.market
            ).eq(
                "symbol", signal.symbol
            ).join(
                "users",  # Join met users tabel
                "signal_preferences.user_id",
                "users.id"
            ).execute()
            
            if response.data:
                self.logger.info(f"Found {len(response.data)} matching subscribers")
                return response.data
            else:
                self.logger.info("No matching subscribers found")
                return []
                
        except Exception as e:
            self.logger.error(f"Error finding matching subscribers: {str(e)}")
            raise 