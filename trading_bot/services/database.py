from supabase import create_client
from datetime import datetime
import logging
import os

logger = logging.getLogger(__name__)

class Database:
    def __init__(self):
        """Initialize database connection"""
        url = os.getenv("SUPABASE_URL")
        key = os.getenv("SUPABASE_KEY")
        
        if not url or not key:
            raise ValueError("Missing Supabase credentials")
            
        self.supabase = create_client(url, key)

    async def save_user_state(self, chat_id: str, state: dict):
        """Save user state using existing columns"""
        try:
            # Converteer state naar database kolommen
            data = {
                'user_id': int(chat_id)
            }
            
            # Voeg alleen bestaande kolommen toe
            if 'market' in state:
                data['market'] = state['market']
            if 'instrument' in state:
                data['instrument'] = state['instrument']
            if 'timeframe' in state:
                data['timeframe'] = state['timeframe']
            
            # Update bestaande rij of maak nieuwe aan
            response = self.supabase.table('subscriber_preferences')\
                .upsert(data)\
                .execute()
            return response.data
            
        except Exception as e:
            logger.error(f"Error saving user state: {str(e)}")
            raise

    async def get_user_state(self, chat_id: str) -> dict:
        """Get user state from existing columns"""
        try:
            response = self.supabase.table('subscriber_preferences')\
                .select('market,instrument,timeframe')\
                .eq('user_id', int(chat_id))\
                .execute()
                
            if response.data:
                # Filter out None values
                return {k: v for k, v in response.data[0].items() if v is not None}
            return {}
            
        except Exception as e:
            logger.error(f"Error getting user state: {str(e)}")
            return {}

    async def save_preference(self, chat_id: str, preference: dict):
        """Save user preference in subscriber_preferences table"""
        try:
            data = {
                'user_id': int(chat_id),
                'market': preference['market'],
                'instrument': preference['instrument'],
                'timeframe': preference['timeframe']
                # created_at en updated_at worden automatisch door Supabase ingevuld
            }
            
            response = self.supabase.table('subscriber_preferences')\
                .insert(data)\
                .execute()
            
            return response.data
            
        except Exception as e:
            logger.error(f"Error saving preference: {str(e)}")
            raise

    async def delete_preference(self, chat_id: str, pref_id: str):
        """Delete user preference from subscriber_preferences table"""
        try:
            response = self.supabase.table('subscriber_preferences')\
                .delete()\
                .eq('id', int(pref_id))\
                .eq('user_id', int(chat_id))\
                .execute()
            
            return response.data
            
        except Exception as e:
            logger.error(f"Error deleting preference: {str(e)}")
            raise 