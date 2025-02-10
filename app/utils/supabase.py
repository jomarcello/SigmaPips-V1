from supabase import create_client, Client
import os
from dotenv import load_dotenv
from app.utils.logger import logger

# Load environment variables
load_dotenv()

# Get Supabase credentials
url = os.getenv("SUPABASE_URL")
key = os.getenv("SUPABASE_KEY")

# Debug logging
logger.debug(f"Initializing Supabase with URL: {url}")
if not url or not key:
    raise ValueError("Missing Supabase credentials in .env file")

# Initialize Supabase client
try:
    # Basic initialization without extra options
    supabase = create_client(url, key)
    logger.info("Supabase client initialized successfully")
except Exception as e:
    logger.error(f"Failed to initialize Supabase client: {str(e)}", exc_info=True)
    raise 