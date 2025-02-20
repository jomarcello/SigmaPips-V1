import logging
import os
from typing import Optional
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import time
import io

logger = logging.getLogger(__name__)

class ChartService:
    def __init__(self):
        self.driver_path = ChromeDriverManager().install()
        logger.info(f"ChromeDriver installed at: {self.driver_path}")
        
    async def generate_chart(self, symbol: str, interval: str) -> Optional[bytes]:
        """Generate chart screenshot for symbol"""
        try:
            logger.info(f"Starting chart generation for {symbol} ({interval})")
            
            # Convert interval to lowercase and map to TradingView format
            interval = self._convert_interval(interval.lower())
            logger.info(f"Using TradingView interval: {interval}")
            
            # Add FX prefix to symbol
            symbol = f"FX:{symbol}"  # FX:EURUSD format
            logger.info(f"Using symbol with prefix: {symbol}")
            
            # Debug: Print environment variables
            logger.info(f"CHROME_BIN: {os.getenv('CHROME_BIN')}")
            logger.info(f"CHROMEDRIVER_PATH: {os.getenv('CHROMEDRIVER_PATH')}")
            
            logger.info("Setting up Chrome options...")
            chrome_options = Options()
            chrome_options.binary_location = os.getenv('CHROME_BIN', '/usr/bin/chromium')
            chrome_options.add_argument('--headless=new')
            chrome_options.add_argument('--no-sandbox')
            chrome_options.add_argument('--disable-dev-shm-usage')
            chrome_options.add_argument('--disable-gpu')
            chrome_options.add_argument('--window-size=1920,1080')
            
            logger.info("Initializing Chrome with options...")
            try:
                service = Service(executable_path=self.driver_path)
                driver = webdriver.Chrome(service=service, options=chrome_options)
                logger.info("Chrome driver initialized successfully")
                
                try:
                    # TradingView URL met correcte parameters
                    url = f"https://www.tradingview.com/chart/?symbol={symbol}&interval={interval}"
                    logger.info(f"Opening URL: {url}")
                    
                    # Get page
                    driver.get(url)
                    logger.info("Waiting for chart to load...")
                    
                    # Wacht tot de chart container geladen is
                    WebDriverWait(driver, 10).until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, 'div[class*="chart-container"]'))
                    )
                    
                    # Zoom in op de chart (meer zoom voor minder grijze randen)
                    logger.info("Zooming chart...")
                    driver.execute_script("""
                        // Zoom in op de chart
                        const chart = document.querySelector('div[class*="chart-container"]');
                        if (chart) {
                            chart.style.transform = 'scale(1.5)';  // 50% inzoomen voor beter resultaat
                            chart.style.transformOrigin = 'center center';
                        }
                    """)
                    
                    # Extra wachttijd voor zoom effect
                    time.sleep(2)
                    
                    # Take screenshot
                    logger.info("Taking screenshot...")
                    screenshot = driver.get_screenshot_as_png()
                    logger.info("Screenshot taken successfully")
                    return screenshot
                    
                finally:
                    logger.info("Closing Chrome driver")
                    driver.quit()
                    
            except Exception as e:
                logger.error(f"Chrome initialization error: {str(e)}", exc_info=True)
                return None
                
        except Exception as e:
            logger.error(f"Error generating chart: {str(e)}", exc_info=True)
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