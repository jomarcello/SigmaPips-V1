# In chart_service.py

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
        
        # ... Chrome setup code ...

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
