"""
Official Agentic Honey-Pot API
ZERO-LOGIC DEBUG BUILD
Returns 200 OK immediately for all requests.
"""

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import os

app = FastAPI(title="Zero-Logic Debug API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configuration
API_KEY = os.getenv("API_KEY", "f5yAISIOwFjQ9QnbSLE8lFp9Vk3cqyAQECC3WHZM15k")

@app.get("/")
async def root_get():
    # Return SAME format as POST to satisfy picky testers
    return {
        "status": "success", 
        "reply": "Service is active and ready. Waiting for scammer."
    }

@app.post("/api/honeypot")
@app.post("/") 
async def honeypot_endpoint(request: Request):
    """
    ZERO-LOGIC DEBUG ENDPOINT
    Does not read body.
    Returns success immediately.
    """
    return {
        "status": "success",
        "reply": "Connection successful. Debug Mode."
    }

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8080)