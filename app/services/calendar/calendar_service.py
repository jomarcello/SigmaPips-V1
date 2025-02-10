import logging
from typing import List

logger = logging.getLogger(__name__)

class CalendarService:
    def __init__(self, db):
        self.db = db
        
    async def get_relevant_events(self, symbol: str) -> List[str]:
        """Get relevant calendar events for symbol"""
        try:
            return [
                "ECB Interest Rate Decision - 14:15",
                "US GDP Data - 15:30"
            ]
        except Exception as e:
            logger.error(f"Error getting events: {str(e)}")
            return [] 