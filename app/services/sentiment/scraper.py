from bs4 import BeautifulSoup
import aiohttp
import logging

class NewsScraper:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
    async def scrape_forex_factory(self, symbol: str) -> list:
        """Scrape ForexFactory news for given symbol"""
        try:
            url = f"https://www.forexfactory.com/news?symbol={symbol}"
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as response:
                    if response.status == 200:
                        html = await response.text()
                        soup = BeautifulSoup(html, 'html.parser')
                        
                        news_items = []
                        for item in soup.select('.news_item'):
                            news_items.append({
                                'title': item.select_one('.title').text.strip(),
                                'time': item.select_one('.time').text.strip(),
                                'impact': item.select_one('.impact').text.strip()
                            })
                            
                        return news_items
                    else:
                        self.logger.error(f"Error scraping ForexFactory: {response.status}")
                        return []
                        
        except Exception as e:
            self.logger.error(f"Error in scrape_forex_factory: {str(e)}")
            return []
            
    async def scrape_investing_com(self, symbol: str) -> list:
        """Scrape Investing.com news for given symbol"""
        try:
            url = f"https://www.investing.com/currencies/{symbol.lower()}-news"
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers=headers) as response:
                    if response.status == 200:
                        html = await response.text()
                        soup = BeautifulSoup(html, 'html.parser')
                        
                        news_items = []
                        for item in soup.select('.articleItem'):
                            news_items.append({
                                'title': item.select_one('.title').text.strip(),
                                'time': item.select_one('.date').text.strip(),
                                'summary': item.select_one('.description').text.strip()
                            })
                            
                        return news_items
                    else:
                        self.logger.error(f"Error scraping Investing.com: {response.status}")
                        return []
                        
        except Exception as e:
            self.logger.error(f"Error in scrape_investing_com: {str(e)}")
            return [] 