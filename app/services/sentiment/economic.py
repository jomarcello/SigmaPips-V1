import aiohttp
from datetime import datetime, timedelta
from bs4 import BeautifulSoup
import logging

logger = logging.getLogger(__name__)

class EconomicCalendar:
    def __init__(self):
        self.logger = logger

    async def get_events(self, symbol: str, days_back: int = 1, days_forward: int = 7) -> list:
        """Get economic events for currency pair"""
        try:
            # Convert symbol (e.g., EURUSD) to currencies (EUR, USD)
            base = symbol[:3]
            quote = symbol[3:]
            
            # Calculate date range
            start_date = (datetime.now() - timedelta(days=days_back)).strftime('%Y-%m-%d')
            end_date = (datetime.now() + timedelta(days=days_forward)).strftime('%Y-%m-%d')
            
            url = f"https://www.forexfactory.com/calendar?day={start_date}"
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as response:
                    if response.status == 200:
                        html = await response.text()
                        events = self._parse_calendar_html(html, base, quote)
                        return events
                    else:
                        self.logger.error(f"Error fetching calendar: {response.status}")
                        return []
                        
        except Exception as e:
            self.logger.error(f"Error in get_events: {str(e)}")
            return []
            
    def _parse_calendar_html(self, html: str, base_currency: str, quote_currency: str) -> list:
        """Parse economic calendar HTML"""
        try:
            soup = BeautifulSoup(html, 'html.parser')
            events = []
            
            for event in soup.select('.calendar__row'):
                currency = event.select_one('.calendar__currency')
                if currency and currency.text.strip() in [base_currency, quote_currency]:
                    events.append({
                        'currency': currency.text.strip(),
                        'event': event.select_one('.calendar__event').text.strip(),
                        'time': event.select_one('.calendar__time').text.strip(),
                        'impact': event.select_one('.calendar__impact').text.strip(),
                        'forecast': event.select_one('.calendar__forecast').text.strip(),
                        'previous': event.select_one('.calendar__previous').text.strip()
                    })
                    
            return events
            
        except Exception as e:
            self.logger.error(f"Error parsing calendar: {str(e)}")
            return [] 