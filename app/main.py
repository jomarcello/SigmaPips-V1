from fastapi import FastAPI
import logging
import sys

# Basic logging setup
logging.basicConfig(
    level=logging.INFO,
    stream=sys.stderr,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize FastAPI
app = FastAPI(title="TradingBot API")

@app.get("/")
async def root():
    return {"status": "online"}

@app.get("/health")
async def health_check():
    logger.info("Health check called")
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=9001) 