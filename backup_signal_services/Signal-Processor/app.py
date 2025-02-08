from fastapi import FastAPI, Request, HTTPException
import os
import logging
import requests
import aiohttp
import asyncio
from typing import Dict, Any

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()

def get_full_url(url: str) -> str:
    """Ensure URL starts with https:// and has no trailing slash"""
    # Remove any trailing slashes from URL
    base_url = url.rstrip('/')
    
    # Add https:// if needed
    if not base_url.startswith(('http://', 'https://')):
        base_url = f"https://{base_url}"
        
    return base_url

async def distribute_signal(signal):
    """Distribute signal to all services"""
    try:
        logger.info(f"Starting to distribute signal: {signal}")
        
        # Get service URLs from environment and ensure they have https://
        telegram_url = get_full_url(os.getenv('TELEGRAM_SERVICE_URL'))
        ai_signal_url = get_full_url(os.getenv('AI_SIGNAL_SERVICE_URL'))
        news_ai_url = get_full_url(os.getenv('NEWS_AI_SERVICE_URL'))
        subscriber_matcher_url = get_full_url(os.getenv('SUBSCRIBER_MATCHER_URL'))
        
        logger.info(f"Using URLs: Telegram={telegram_url}, AI={ai_signal_url}, News={news_ai_url}, Matcher={subscriber_matcher_url}")
        
        # Send to subscriber matcher first to get chat_ids
        async with aiohttp.ClientSession() as session:
            try:
                async with session.post(subscriber_matcher_url, json=signal) as resp:
                    if resp.status == 200:
                        subscriber_data = await resp.json()
                        chat_ids = subscriber_data.get('matched_subscribers', [])
                        signal['chat_ids'] = [sub['chat_id'] for sub in chat_ids]
                    else:
                        error_text = await resp.text()
                        logger.error(f"Subscriber matcher error: {error_text}")
            except Exception as e:
                logger.error(f"Error calling subscriber matcher: {str(e)}")
            
            # Now send to other services with chat_ids
            tasks = []
            
            # Send to AI Signal Service
            tasks.append(session.post(
                ai_signal_url,
                json=signal,
                ssl=False
            ))
            
            # Send to News AI Service
            tasks.append(session.post(
                news_ai_url,
                json=signal,
                ssl=False
            ))
            
            # Send to Telegram Service
            tasks.append(session.post(
                telegram_url,
                json=signal,
                ssl=False
            ))
            
            # Rest of the code... 