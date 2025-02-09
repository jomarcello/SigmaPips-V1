import os
import logging
from fastapi import FastAPI, Request

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Initialize FastAPI
app = FastAPI()

@app.get("/health")
async def health():
    """Basic health check"""
    logger.info("Health check called")
    return {"status": "ok", "message": "Service is running"}

@app.post("/webhook")
async def webhook(request: Request):
    """Minimal webhook handler"""
    try:
        # Return immediately
        logger.info("Webhook called")
        return {"ok": True, "message": "Webhook received"}
    except Exception as e:
        logger.error(f"Error: {e}")
        return {"ok": False, "error": str(e)}

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8080))
    logger.info(f"Starting server on port {port}")
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=port,
        log_level="debug",
        timeout_keep_alive=65,
        limit_concurrency=100
    )
