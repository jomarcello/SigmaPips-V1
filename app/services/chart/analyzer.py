from app.services.signal_processor.models import TradingSignal
from app.utils.logger import logger
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import os
import time
from datetime import datetime
import io

class ChartAnalyzer:
    def __init__(self):
        self.logger = logger
        self._setup_chrome()

    def _setup_chrome(self):
        """Setup Chrome with correct options"""
        chrome_options = Options()
        chrome_options.add_argument("--start-maximized")  # Start in fullscreen
        chrome_options.add_argument("--disable-infobars")  # Remove info bars
        chrome_options.add_argument("--hide-scrollbars")  # Hide scrollbars
        chrome_options.add_argument("--headless")         # Run in background
        chrome_options.add_argument("--window-size=1920,1080")
        self.driver = webdriver.Chrome(options=chrome_options)

    async def generate_chart(self, instrument: str) -> bytes:
        """Generate chart screenshot"""
        try:
            self.logger.info(f"📸 Taking screenshot for {instrument}")
            
            # Create TradingView URL with clean chart parameters
            url = (
                f"https://www.tradingview.com/chart?"
                f"symbol=FX:{instrument}&"
                "theme=light&"
                "hidevolume=1&"
                "hidesidetoolbar=1"
            )
            
            # Load page
            self.driver.get(url)
            time.sleep(8)  # Wait for chart to load
            
            # Hide UI elements and maximize chart
            self.driver.execute_script("""
                // Hide all UI elements
                document.querySelector('body').style.overflow = 'hidden';
                
                // Remove all toolbars and panels
                [
                    '.tv-header',
                    '.tv-side-toolbar',
                    '.tv-bottom-toolbar',
                    '.chart-controls-bar',
                    '.layout__area--top',
                    '.layout__area--left',
                    '.layout__area--right',
                    '.layout__area--bottom'
                ].forEach(selector => {
                    const elements = document.querySelectorAll(selector);
                    elements.forEach(el => el && el.remove());
                });
                
                // Maximize chart container
                const chart = document.querySelector('.chart-container');
                if (chart) {
                    chart.style.position = 'fixed';
                    chart.style.top = '0';
                    chart.style.left = '0';
                    chart.style.width = '100vw';
                    chart.style.height = '100vh';
                    chart.style.margin = '0';
                    chart.style.padding = '0';
                    chart.style.zIndex = '9999';
                }
                
                // Force resize
                window.dispatchEvent(new Event('resize'));
            """)
            
            time.sleep(2)  # Wait for UI changes
            
            # Find and screenshot only the chart element
            chart_element = self.driver.find_element("css selector", ".chart-container")
            screenshot = chart_element.screenshot_as_png
            
            self.logger.info(f"✅ Screenshot taken for {instrument}")
            return screenshot
            
        except Exception as e:
            self.logger.error(f"❌ Screenshot error: {str(e)}")
            raise

    async def get_technical_analysis(self, instrument: str) -> dict:
        """Get technical analysis data"""
        try:
            # Simplified version - return basic data
            return {
                "d": [
                    0.7,  # Overall rating
                    65,   # RSI
                    64,   # RSI[1]
                    75,   # Stoch.K
                    70,   # Stoch.D
                    0.002,# MACD
                    0.001 # MACD Signal
                ]
            }
                    
        except Exception as e:
            self.logger.error(f"Error getting technical analysis: {str(e)}", exc_info=True)
            raise 