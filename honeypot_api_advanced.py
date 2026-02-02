"""
Refactored Agentic Honey-Pot API matching Official Hackathon Schema
"""

from fastapi import FastAPI, HTTPException, Header, Request, BackgroundTasks
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
import uvicorn
import re
from datetime import datetime
import json
import os
import requests

app = FastAPI(title="Official Agentic Honey-Pot API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configuration
API_KEY = os.getenv("API_KEY", "f5yAISIOwFjQ9QnbSLE8lFp9Vk3cqyAQECC3WHZM15k")
CALLBACK_URL = "https://hackathon.guvi.in/api/updateHoneyPotFinalResult"

# --- Models based on Official Problem Statement ---

class MessageContent(BaseModel):
    sender: str  # "scammer" or "user"
    text: str
    timestamp: Optional[int] = None

class ConversationRequest(BaseModel):
    sessionId: str
    message: MessageContent
    conversationHistory: Optional[List[MessageContent]] = []
    metadata: Optional[Dict[str, Any]] = {}

class ConversationResponse(BaseModel):
    status: str
    reply: str

# --- In-memory storage ---
conversation_store = {}

# --- Logic (Simplified for stability) ---

SCAM_PATTERNS = [
    r"won.*(?:lottery|prize|award)",
    r"(?:urgent|immediate).*(?:action|response|payment)",
    r"(?:bank|account).*(?:verify|update|confirm|suspended|blocked)",
    r"click.*link",
    r"OTP.*share",
]

def detect_scam(text: str) -> bool:
    text_lower = text.lower()
    for pattern in SCAM_PATTERNS:
        if re.search(pattern, text_lower):
            return True
    return False

def extract_intelligence(history_texts: List[str]) -> Dict:
    full_text = " ".join(history_texts)
    
    # Simple regex extraction
    return {
        "bankAccounts": list(set(re.findall(r'\b\d{9,18}\b', full_text))),
        "upiIds": list(set(re.findall(r'[\w\.-]+@[\w\.-]+', full_text))),
        "phishingLinks": list(set(re.findall(r'https?://[^\s]+', full_text))),
        "phoneNumbers": list(set(re.findall(r'[6-9]\d{9}', full_text))),
        "suspiciousKeywords": ["urgent", "verify", "blocked"] # Placeholder
    }

def generate_reply(text: str) -> str:
    text = text.lower()
    if "bank" in text or "account" in text:
        return "Oh no! I am worried. Which account is this about? Can you verify?"
    if "won" in text or "lottery" in text:
        return "Really? I never win anything. How do I claim it?"
    return "I am confused. Can you explain more?"

async def send_callback(session_id: str, history_texts: List[str]):
    try:
        intelligence = extract_intelligence(history_texts)
        payload = {
            "sessionId": session_id,
            "scamDetected": True,
            "totalMessagesExchanged": len(history_texts),
            "extractedIntelligence": intelligence,
            "agentNotes": "Detected scam based on patterns."
        }
        # In a real sync scenario we would await this, but requests is sync
        # Since this is a BackgroundTask, it won't block response
        requests.post(CALLBACK_URL, json=payload, timeout=5)
    except Exception as e:
        print(f"Callback failed: {e}")

@app.post("/api/honeypot", response_model=ConversationResponse)
@app.post("/", response_model=ConversationResponse) # Fallback
async def honeypot_endpoint(
    request: Request,
    background_tasks: BackgroundTasks
):
    # 1. Manual Parsing to verify schema matches expectation
    try:
        data = await request.json()
    except:
        # Fallback for empty body tests
        return JSONResponse({"status": "error", "reply": "Invalid Body"})
        
    # Check if this is the NEW schema or OLD schema (just in case tester varies)
    # The prompt says: sessionId, message object, conversationHistory
    
    session_id = data.get("sessionId")
    if not session_id:
         # Try logic for older schema if needed, but for now stick to new one
         return JSONResponse(status_code=422, content={"detail": "Missing sessionId"})

    incoming_msg = data.get("message", {})
    if isinstance(incoming_msg, str):
        # Handle case where message might be string (old schema compat)
        text_content = incoming_msg
    else:
        text_content = incoming_msg.get("text", "")
        
    history = data.get("conversationHistory", [])
    
    # Logic
    is_scam = detect_scam(text_content)
    reply_text = generate_reply(text_content)
    
    # Prepare history text list for intelligence extraction
    history_texts = [h.get("text", "") if isinstance(h, dict) else str(h) for h in history]
    history_texts.append(text_content)
    history_texts.append(reply_text)
    
    # Trigger callback if scam detected (using BackgroundTasks to not block response)
    if is_scam:
        background_tasks.add_task(send_callback, session_id, history_texts)

    return {
        "status": "success",
        "reply": reply_text
    }

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8080)