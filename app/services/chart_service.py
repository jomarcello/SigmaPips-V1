import logging
import os
from typing import Optional
from tradingview_ta import TA_Handler
from PIL import Image
import io
import aiohttp

logger = logging.getLogger(__name__)

class ChartService:
    def __init__(self):
        self.tradingview_token = os.getenv("TRADINGVIEW_TOKEN")
        
    async def generate_chart(self, symbol: str, interval: str) -> Optional[bytes]:
        """Generate chart image for symbol"""
        try:
            # Initialize TradingView handler
            handler = TA_Handler(
                symbol=symbol,
                screener="forex" if "USD" in symbol else "crypto",
                exchange="OANDA" if "USD" in symbol else "BINANCE",
                interval=self._convert_interval(interval)
            )
            
            # Get chart URL
            chart_url = f"https://www.tradingview.com/chart/?symbol={symbol}&interval={interval}"
            
            # Download chart image
            async with aiohttp.ClientSession() as session:
                async with session.get(chart_url, headers={
                    "Authorization": f"Bearer {self.tradingview_token}"
                }) as response:
                    if response.status == 200:
                        image_data = await response.read()
                        
                        # Process image
                        img = Image.open(io.BytesIO(image_data))
                        
                        # Add indicators
                        analysis = handler.get_analysis()
                        
                        # Convert to bytes
                        img_byte_arr = io.BytesIO()
                        img.save(img_byte_arr, format='PNG')
                        img_byte_arr = img_byte_arr.getvalue()
                        
                        return img_byte_arr
                    else:
                        logger.error(f"Error getting chart: {response.status}")
                        return None
                        
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