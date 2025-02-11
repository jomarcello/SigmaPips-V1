from supabase import create_client
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class Database:
    def __init__(self, url: str, key: str):
        self.supabase = create_client(url, key)

    async def save_user_state(self, chat_id: str, state: dict):
        """Save user state in subscriber_preferences table"""
        try:
            # Update bestaande preference of maak nieuwe aan
            data = {
                'user_id': int(chat_id),
                'state': state,
                'updated_at': datetime.now().isoformat()
            }
            
            response = self.supabase.table('subscriber_preferences')\
                .upsert(data)\
                .execute()
            return response.data
            
        except Exception as e:
            logger.error(f"Error saving user state: {str(e)}")
            raise

    async def get_user_state(self, chat_id: str) -> dict:
        """Get user state from subscriber_preferences table"""
        try:
            response = self.supabase.table('subscriber_preferences')\
                .select('state')\
                .eq('user_id', int(chat_id))\
                .execute()
                
            if response.data and 'state' in response.data[0]:
                return response.data[0]['state']
            return {}
            
        except Exception as e:
            logger.error(f"Error getting user state: {str(e)}")
            return {}  # Return empty state on error 

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