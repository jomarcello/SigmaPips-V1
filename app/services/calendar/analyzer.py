from datetime import datetime
import aiohttp
import logging
import os
from openai import AsyncOpenAI

logger = logging.getLogger(__name__)

class EconomicCalendar:
    def __init__(self):
        self.perplexity_key = os.getenv("PERPLEXITY_API_KEY")
        self.openai_client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        
    async def get_events(self) -> str:
        """Get economic calendar events for today"""
        try:
            # Get raw events from Perplexity
            events_data = await self._get_perplexity_events()
            
            # Format with OpenAI
            formatted_events = await self._format_with_openai(events_data)
            
            return formatted_events
            
        except Exception as e:
            logger.error(f"Error getting calendar events: {str(e)}")
            return "Error fetching economic calendar"
            
    async def _get_perplexity_events(self) -> str:
        """Get raw events data from Perplexity AI"""
        try:
            url = "https://api.perplexity.ai/chat/completions"
            today = datetime.utcnow().strftime("%Y-%m-%d")
            
            headers = {
                "Authorization": f"Bearer {self.perplexity_key}",
                "Content-Type": "application/json"
            }
            
            payload = {
                "model": "sonar-pro",
                "messages": [{
                    "role": "system",
                    "content": "You are an economic data provider. Return only raw economic calendar data."
                }, {
                    "role": "user", 
                    "content": f"""Get today's ({today}) economic calendar events. For each event, provide:
                    - Exact time (UTC)
                    - Event name
                    - Currency affected
                    - Impact level (High/Medium/Low)
                    - Forecast value (if available)
                    - Previous value (if available)

                    Include only real, verified events. No formatting needed."""
                }],
                "temperature": 0.1
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(url, json=payload, headers=headers) as response:
                    if response.status == 200:
                        data = await response.json()
                        return data['choices'][0]['message']['content']
                    else:
                        raise Exception(f"Perplexity API error: {response.status}")
                        
        except Exception as e:
            logger.error(f"Error getting events from Perplexity: {str(e)}")
            return ""
            
    async def _format_with_openai(self, events_data: str) -> str:
        """Format events with OpenAI for better presentation"""
        try:
            response = await self.openai_client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are an expert in formatting economic calendar data in a clean, readable format."},
                    {"role": "user", "content": f"""Format these economic events in a clean, readable format:

{events_data}

Format like this:

📅 <b>Economic Calendar</b>

🔴 <b>High Impact Events:</b>
• 08:00 UTC | German CPI (MoM) | EUR
  Forecast: 0.4% | Previous: 0.3%

• 12:30 UTC | US Non-Farm Payrolls | USD
  Forecast: 200K | Previous: 180K

🟡 <b>Medium Impact Events:</b>
• 15:30 UTC | Oil Inventories | USD
  Forecast: -1.2M | Previous: -1.5M

⚪ <b>Low Impact Events:</b>
• 23:50 UTC | Japan GDP (QoQ) | JPY
  Forecast: 0.5% | Previous: 0.3%

Rules:
1. Use bullet points and clean spacing
2. Use impact emojis: 🔴 High, 🟡 Medium, ⚪ Low
3. Group events by impact level
4. If no events, respond: "No major economic events scheduled for today."
5. Keep it simple and readable
6. Only use HTML tags that Telegram supports (<b> and line breaks)"""
                }],
                temperature=0.3
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            logger.error(f"Error formatting with OpenAI: {str(e)}")
            return "Error formatting economic calendar"

    async def _scrape_forex_factory(self) -> list:
        """Scrape economic calendar from ForexFactory"""
        try:
            url = "https://www.forexfactory.com/calendar"
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as response:
                    if response.status == 200:
                        html = await response.text()
                        return self._parse_calendar_html(html)
                    else:
                        raise Exception(f"Error fetching calendar: {response.status}")
                        
        except Exception as e:
            logger.error(f"Error scraping ForexFactory: {str(e)}")
            return []
            
    def _parse_calendar_html(self, html: str) -> list:
        """Parse ForexFactory calendar HTML"""
        events = []
        soup = BeautifulSoup(html, 'html.parser')
        
        today = datetime.utcnow().strftime('%Y-%m-%d')
        
        for row in soup.select('.calendar__row'):
            try:
                date = row.select_one('.calendar__date')
                if date and date.text.strip() == today:
                    time = row.select_one('.calendar__time').text.strip()
                    currency = row.select_one('.calendar__currency').text.strip()
                    event = row.select_one('.calendar__event').text.strip()
                    impact = row.select_one('.calendar__impact')['title'].strip()
                    forecast = row.select_one('.calendar__forecast').text.strip() or '-'
                    previous = row.select_one('.calendar__previous').text.strip() or '-'
                    
                    # Convert impact to emoji
                    impact_emoji = {
                        'High Impact Expected': '🔴 High',
                        'Medium Impact Expected': '🟡 Medium',
                        'Low Impact Expected': '⚪ Low'
                    }.get(impact, '⚪ Low')
                    
                    events.append({
                        'time': time,
                        'event': event,
                        'currency': currency,
                        'impact': impact_emoji,
                        'forecast': forecast,
                        'previous': previous
                    })
                    
            except Exception as e:
                logger.error(f"Error parsing event row: {str(e)}")
                continue
                
        return events
        
    def _format_events(self, events: list) -> str:
        """Format events as a nice table"""
        if not events:
            return "No major economic events scheduled for today."
            
        # Sort events by impact
        high_impact = []
        medium_impact = []
        low_impact = []
        
        for event in events:
            if '🔴' in event['impact']:
                high_impact.append(event)
            elif '🟡' in event['impact']:
                medium_impact.append(event)
            else:
                low_impact.append(event)
                
        # Format table
        table = f"📅 <b>Economic Calendar</b> ({datetime.utcnow().strftime('%Y-%m-%d')})\n\n"
        
        if high_impact:
            table += "🔴 <b>High Impact Events:</b>\n"
            for event in high_impact:
                table += f"• {event['time']} UTC | {event['event']} | {event['currency']}\n  Forecast: {event['forecast']} | Previous: {event['previous']}\n"
            
        if medium_impact:
            table += "🟡 <b>Medium Impact Events:</b>\n"
            for event in medium_impact:
                table += f"• {event['time']} UTC | {event['event']} | {event['currency']}\n  Forecast: {event['forecast']} | Previous: {event['previous']}\n"
            
        if low_impact:
            table += "⚪ <b>Low Impact Events:</b>\n"
            for event in low_impact:
                table += f"• {event['time']} UTC | {event['event']} | {event['currency']}\n  Forecast: {event['forecast']} | Previous: {event['previous']}\n"
            
        return table 