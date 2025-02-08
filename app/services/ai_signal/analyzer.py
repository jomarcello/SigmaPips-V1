from app.services.signal_processor.models import TradingSignal
from app.utils.logger import logger
import os
from openai import AsyncOpenAI

class AISignalAnalyzer:
    def __init__(self):
        self.logger = logger
        self.client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))

    async def analyze_signal(self, signal: TradingSignal) -> str:
        """Analyze trading signal using AI"""
        try:
            # Create prompt for AI
            prompt = self._create_analysis_prompt(signal)
            
            # Get AI analysis
            response = await self.client.chat.completions.create(
                model="gpt-4-turbo-preview",
                messages=[
                    {"role": "system", "content": "You are an expert trading analyst. Analyze the given trading signal and provide clear, concise insights and recommendations."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=500
            )
            
            analysis = response.choices[0].message.content
            self.logger.info(f"AI analysis generated for {signal.instrument}")
            return analysis
            
        except Exception as e:
            self.logger.error(f"Error in AI analysis: {str(e)}", exc_info=True)
            raise

    def _create_analysis_prompt(self, signal: TradingSignal) -> str:
        """Create prompt for AI analysis"""
        return f"""
You are SigmaPips AI. Analyze the following technical data and provide ONLY a verdict in 2-3 sentences. Do not include any headers, sections, or formatting:

Technical Data:
- RSI: {signal.additional_info.get('rsi')}
- MA Fast: {signal.additional_info.get('ma_fast')}
- MA Slow: {signal.additional_info.get('ma_slow')}

Focus on:
1. Momentum analysis
2. Key technical levels
3. Risk/reward assessment
4. Potential risks or concerns
""" 