import logging
import os
from typing import Optional
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import time
import io

logger = logging.getLogger(__name__)

class ChartService:
    def __init__(self):
        self.chrome_options = self._setup_chrome_options()
        
    def _setup_chrome_options(self):
        chrome_options = Options()
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--window-size=1920,1080')
        return chrome_options
        
    async def generate_chart(self, symbol: str, interval: str) -> Optional[bytes]:
        """Generate chart screenshot for symbol"""
        try:
            # Setup Chrome
            driver = webdriver.Chrome(options=self.chrome_options)
            
            try:
                # TradingView URL
                url = f"https://www.tradingview.com/chart/?symbol={symbol}&interval={interval}"
                
                # Get page
                driver.get(url)
                time.sleep(5)  # Wait for chart to load
                
                # Take screenshot
                screenshot = driver.get_screenshot_as_png()
                return screenshot
                
            finally:
                driver.quit()
                
        except Exception as e:
            logger.error(f"Error generating chart: {str(e)}")
            return None
            
    def _convert_interval(self, interval: str) -> str:
        """Convert interval to TradingView format"""
        mapping = {
            "1m": "1",
            "5m": "5",
            "15m": "15",
            "30m": "30",
            "1h": "60",
            "4h": "240",
            "1d": "1D"
        }
        return mapping.get(interval, "60")  # Default to 1h 