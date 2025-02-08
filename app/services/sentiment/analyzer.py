from openai import AsyncOpenAI
import aiohttp
import os
import json
import logging

logger = logging.getLogger(__name__)

class SentimentAnalyzer:
    def __init__(self):
        self.openai_client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.perplexity_key = os.getenv("PERPLEXITY_API_KEY")
        
    async def analyze(self, symbol: str) -> str:
        """Analyze market sentiment using Perplexity and OpenAI"""
        try:
            # Step 1: Get news from Perplexity
            news_data = await self._get_perplexity_news(symbol)
            
            if not news_data:
                raise Exception("No news data available")
                
            # Step 2: Format news for OpenAI
            formatted_news = self._format_news_for_openai(news_data)
            
            # Step 3: Get sentiment analysis from OpenAI
            sentiment = await self._get_openai_analysis(symbol, formatted_news)
            
            return sentiment
            
        except Exception as e:
            logger.error(f"Error in analyze: {str(e)}")
            return "Error analyzing market sentiment"
            
    async def _get_perplexity_news(self, symbol: str) -> dict:
        """Get news from Perplexity AI"""
        try:
            url = "https://api.perplexity.ai/chat/completions"
            
            headers = {  # Define headers here
                "Authorization": f"Bearer {self.perplexity_key}",
                "Content-Type": "application/json"
            }
            
            payload = {
                "model": "sonar-pro",
                "messages": [{
                    "role": "system",
                    "content": "You are a financial market analyst providing news summaries."
                }, {
                    "role": "user", 
                    "content": f"""Analyze the latest market news for {symbol} forex pair.

                    Format your response as:
                    Title: [article title]
                    Date: [publication date]
                    Source: [news source]
                    Summary: [brief summary, max 3 sentences]
                    Impact: [specific impact on {symbol} price]

                    Provide at least 3 recent, high-impact news items."""
                }],
                "temperature": 0.7,
                "top_p": 1,
                "max_tokens": 1000
            }
            
            logger.debug(f"Making Perplexity API call for {symbol}")
            logger.debug(f"Using token: {self.perplexity_key[:8]}...{self.perplexity_key[-4:]}")
            
            async with aiohttp.ClientSession() as session:
                async with session.post(url, json=payload, headers=headers) as response:
                    if response.status == 200:
                        data = await response.json()
                        logger.info("✅ Perplexity API call successful")
                        return self._parse_perplexity_response(data['choices'][0]['message']['content'])
                    else:
                        error_text = await response.text()
                        logger.error(f"Perplexity API error response: {error_text}")
                        raise Exception(f"Perplexity API error: {response.status}")
                        
        except Exception as e:
            logger.error(f"Error getting news from Perplexity: {str(e)}")
            return {}
            
    def _parse_perplexity_response(self, content: str) -> dict:
        """Parse Perplexity response into structured format"""
        try:
            # Convert text to JSON structure
            news_items = []
            current_item = {}
            
            for line in content.split('\n'):
                if line.startswith('Title:'):
                    if current_item:
                        news_items.append(current_item)
                    current_item = {'title': line[6:].strip()}
                elif line.startswith('Date:'):
                    current_item['date'] = line[5:].strip()
                elif line.startswith('Source:'):
                    current_item['source'] = line[7:].strip()
                elif line.startswith('Summary:'):
                    current_item['summary'] = line[8:].strip()
                elif line.startswith('Impact:'):
                    current_item['impact'] = line[7:].strip()
                    
            if current_item:
                news_items.append(current_item)
                
            return {'news': news_items}
            
        except Exception as e:
            logger.error(f"Error parsing Perplexity response: {str(e)}")
            return {'news': []}
            
    async def _get_openai_analysis(self, symbol: str, news_data: str) -> str:
        """Get sentiment analysis from OpenAI"""
        try:
            prompt = f"""Analyze the following news about {symbol}:

{news_data}

Provide your analysis in exactly this format:

📈 Market Sentiment:
• Direction: [Bullish/Bearish/Neutral]
• Strength: [Strong/Moderate/Weak]
• Key drivers: [Summary of main news drivers]

💡 Trading Implications:
• Short-term outlook
• Risks and opportunities
• Key price levels to watch

⚠️ Risk Factors:
• List at least 2 key risks
• Focus on economic factors

🎯 Conclusion:
Brief summary and trading strategy"""

            response = await self.openai_client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are an expert forex analyst specializing in market sentiment analysis."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            logger.error(f"Error getting OpenAI analysis: {str(e)}")
            raise
            
    def _format_news_for_openai(self, news_data: dict) -> str:
        """Format news data for OpenAI prompt"""
        formatted_news = []
        
        for item in news_data.get('news', []):
            formatted_news.append(
                f"📰 {item['title']}\n"
                f"📅 {item['date']}\n"
                f"📱 {item['source']}\n"
                f"📝 {item['summary']}\n"
                f"📊 Impact: {item['impact']}\n"
            )
            
        return "\n\n".join(formatted_news) 