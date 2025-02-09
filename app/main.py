from fastapi import FastAPI
import os

# Initialize FastAPI met basis configuratie
app = FastAPI()

@app.get("/health")
async def health_check():
    return {"status": "ok"}

# Verwijder __main__ block omdat Railway uvicorn direct start 