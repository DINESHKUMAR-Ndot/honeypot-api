"""
Agentic Honey-Pot API for Scam Detection and Intelligence Extraction
This API detects scam messages and autonomously engages scammers to extract intelligence.
"""

from fastapi import FastAPI, HTTPException, Header, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
import uvicorn
import re
from datetime import datetime
import json

app = FastAPI(
    title="Agentic Honey-Pot API",
    description="AI-powered scam detection and intelligence extraction system",
    version="1.0.0"
)

# Configuration
API_KEY = "PV8QLLXOKKF-RrUTQXsElrj1etm7k4I2PTm1OMlRGxg"  # Change this to your actual API key

# In-memory conversation storage
conversation_history: Dict[str, List[Dict]] = {}

# Scam patterns for detection
SCAM_PATTERNS = [
    r"won.*(?:lottery|prize|award)",
    r"(?:urgent|immediate).*(?:action|response|payment)",
    r"(?:bank|account).*(?:verify|update|confirm|suspended|blocked)",
    r"click.*(?:link|here|now)",
    r"(?:congratulations|winner|selected)",
    r"limited.*(?:time|offer)",
    r"(?:claim|collect).*(?:prize|reward|money)",
    r"(?:tax|customs|clearance).*(?:fee|payment|charge)",
    r"OTP.*(?:share|send|provide)",
    r"UPI.*(?:ID|pin|password)",
    r"transfer.*(?:money|amount|funds)",
    r"refund.*(?:processing|pending)",
    r"KYC.*(?:update|pending|expired)",
]

# Persona templates for the agent
PERSONAS = {
    "elderly": {
        "name": "Ramesh Kumar",
        "age": 67,
        "traits": "retired, not tech-savvy, trusting, eager to help",
        "speech_pattern": "polite, asks clarifying questions, types slowly"
    },
    "busy_professional": {
        "name": "Priya Sharma",
        "age": 35,
        "traits": "working mother, busy, distracted, wants quick solutions",
        "speech_pattern": "brief responses, occasional typos, multitasking"
    },
    "student": {
        "name": "Arjun Patel",
        "age": 21,
        "traits": "college student, somewhat tech-aware but naive about scams",
        "speech_pattern": "casual, uses abbreviations, curious"
    }
}


class Message(BaseModel):
    role: str = Field(..., description="Either 'user' (scammer) or 'assistant' (honeypot)")
    content: str = Field(..., description="Message content")
    timestamp: Optional[str] = Field(default=None, description="Message timestamp")


class ConversationRequest(BaseModel):
    conversation_id: str = Field(..., description="Unique conversation identifier")
    message: str = Field(..., description="Incoming message from scammer")
    conversation_history: Optional[List[Message]] = Field(default=[], description="Previous messages")
    metadata: Optional[Dict[str, Any]] = Field(default={}, description="Additional metadata")


class ExtractedIntelligence(BaseModel):
    bank_accounts: List[str] = Field(default=[], description="Extracted bank account numbers")
    upi_ids: List[str] = Field(default=[], description="Extracted UPI IDs")
    phone_numbers: List[str] = Field(default=[], description="Extracted phone numbers")
    urls: List[str] = Field(default=[], description="Extracted URLs/links")
    other_data: Dict[str, Any] = Field(default={}, description="Other extracted information")


class ConversationResponse(BaseModel):
    conversation_id: str
    is_scam: bool
    confidence: float = Field(..., ge=0.0, le=1.0)
    agent_engaged: bool
    response_message: str
    turn_count: int
    extracted_intelligence: ExtractedIntelligence
    scam_type: Optional[str] = None
    reasoning: str


def verify_api_key(x_api_key: str = Header(...)):
    """Verify API key from header"""
    if x_api_key != API_KEY:
        raise HTTPException(status_code=401, detail="Invalid API key")
    return x_api_key


def detect_scam(message: str, history: List[Message]) -> tuple[bool, float, str]:
    """
    Detect if message contains scam indicators
    Returns: (is_scam, confidence, scam_type)
    """
    message_lower = message.lower()
    
    # Check against patterns
    pattern_matches = 0
    matched_patterns = []
    
    for pattern in SCAM_PATTERNS:
        if re.search(pattern, message_lower, re.IGNORECASE):
            pattern_matches += 1
            matched_patterns.append(pattern)
    
    # Scam indicators
    scam_keywords = [
        'lottery', 'winner', 'prize', 'claim', 'urgent', 'verify',
        'suspended', 'blocked', 'otp', 'bank account', 'upi', 'transfer',
        'refund', 'kyc', 'congratulations', 'selected', 'tax', 'fee',
        'payment', 'clearance', 'link', 'click here'
    ]
    
    keyword_count = sum(1 for keyword in scam_keywords if keyword in message_lower)
    
    # Calculate confidence
    confidence = min(0.95, (pattern_matches * 0.15 + keyword_count * 0.05))
    
    # Determine scam type
    scam_type = None
    if any(word in message_lower for word in ['lottery', 'prize', 'won']):
        scam_type = "lottery_scam"
    elif any(word in message_lower for word in ['bank', 'account', 'kyc']):
        scam_type = "banking_scam"
    elif any(word in message_lower for word in ['otp', 'verify', 'code']):
        scam_type = "otp_scam"
    elif any(word in message_lower for word in ['refund', 'payment', 'transfer']):
        scam_type = "payment_scam"
    
    is_scam = confidence >= 0.3 or pattern_matches >= 2
    
    return is_scam, confidence, scam_type


def extract_intelligence(text: str, history: List[Message]) -> ExtractedIntelligence:
    """Extract intelligence from messages"""
    intelligence = ExtractedIntelligence()
    
    # Extract bank account numbers (9-18 digits)
    bank_pattern = r'\b\d{9,18}\b'
    bank_accounts = re.findall(bank_pattern, text)
    intelligence.bank_accounts = list(set(bank_accounts))
    
    # Extract UPI IDs
    upi_pattern = r'\b[\w\.-]+@[\w\.-]+\b'
    upi_ids = [match for match in re.findall(upi_pattern, text) 
               if any(provider in match.lower() for provider in ['paytm', 'phonepe', 'gpay', 'upi', 'ybl', 'okhdfcbank', 'okicici', 'okaxis'])]
    intelligence.upi_ids = list(set(upi_ids))
    
    # Extract phone numbers
    phone_pattern = r'\b(?:\+91|91)?[6-9]\d{9}\b'
    phones = re.findall(phone_pattern, text)
    intelligence.phone_numbers = list(set(phones))
    
    # Extract URLs
    url_pattern = r'https?://[^\s]+'
    urls = re.findall(url_pattern, text)
    intelligence.urls = list(set(urls))
    
    # Extract IFSC codes
    ifsc_pattern = r'\b[A-Z]{4}0[A-Z0-9]{6}\b'
    ifsc_codes = re.findall(ifsc_pattern, text)
    if ifsc_codes:
        intelligence.other_data['ifsc_codes'] = list(set(ifsc_codes))
    
    # Also check conversation history
    for msg in history:
        if msg.role == "user":
            # Extract from previous scammer messages
            bank_accounts.extend(re.findall(bank_pattern, msg.content))
            upi_matches = re.findall(upi_pattern, msg.content)
            upi_ids.extend([m for m in upi_matches if any(p in m.lower() for p in ['paytm', 'phonepe', 'gpay', 'upi', 'ybl'])])
            urls.extend(re.findall(url_pattern, msg.content))
    
    # Deduplicate
    intelligence.bank_accounts = list(set(intelligence.bank_accounts))
    intelligence.upi_ids = list(set(intelligence.upi_ids))
    intelligence.urls = list(set(intelligence.urls))
    
    return intelligence


def generate_agent_response(
    message: str, 
    history: List[Message], 
    scam_type: str,
    persona_type: str = "elderly"
) -> str:
    """
    Generate contextual response from AI agent
    This simulates an LLM-powered agent response
    """
    persona = PERSONAS[persona_type]
    turn_count = len([m for m in history if m.role == "assistant"])
    
    message_lower = message.lower()
    
    # Response strategies based on turn count
    if turn_count == 0:
        # First response - express interest
        responses = [
            f"Hello! I received your message. Can you please explain this in more detail?",
            f"Oh my! Is this really true? How does this work?",
            f"I'm interested but I don't understand completely. Can you help me?"
        ]
        return responses[hash(message) % len(responses)]
    
    elif turn_count == 1:
        # Second response - show some concern but remain engaged
        responses = [
            f"This sounds interesting. What do I need to do exactly?",
            f"I want to proceed but I'm not very good with technology. Can you guide me step by step?",
            f"Okay, I understand a little bit. What information do you need from me?"
        ]
        return responses[hash(message) % len(responses)]
    
    elif turn_count == 2:
        # Third response - ask about payment/transfer details
        if 'account' in message_lower or 'bank' in message_lower:
            return "I need to transfer money? To which account should I send it? Please share the account details."
        elif 'upi' in message_lower:
            return "You want me to send via UPI? What is your UPI ID? I use Google Pay."
        elif 'link' in message_lower or 'click' in message_lower:
            return "There's a link? Can you send it again? Sometimes my phone doesn't show links properly."
        else:
            return "What payment method should I use? I have bank account and UPI both."
    
    elif turn_count == 3:
        # Fourth response - ask for confirmation of details
        return "Let me confirm the details you shared. Can you please repeat the account number/UPI ID? I want to make sure I send to the correct place."
    
    elif turn_count >= 4:
        # Later responses - stall with technical difficulties or questions
        delay_responses = [
            "I'm trying but getting some error. Can you share the details again?",
            "My bank app is not working. Do you have another account number?",
            "The UPI payment failed. Do you have PhonePe or Paytm ID also?",
            "I need to verify this with my son first. Can you send me a screenshot or proof?",
            "One moment, let me check my account balance. What was the exact amount needed?"
        ]
        return delay_responses[turn_count % len(delay_responses)]
    
    return "I see. Please tell me what to do next."


@app.get("/")
async def root():
    """Root endpoint - API health check"""
    return {
        "status": "active",
        "service": "Agentic Honey-Pot API",
        "version": "1.0.0",
        "timestamp": datetime.now().isoformat()
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "active_conversations": len(conversation_history)
    }


@app.post("/api/honeypot", response_model=ConversationResponse)
async def honeypot_endpoint(
    request: ConversationRequest,
    x_api_key: str = Header(..., alias="x-api-key")
):
    """
    Main honeypot endpoint that receives scam messages and responds intelligently
    """
    # Verify API key
    verify_api_key(x_api_key)
    
    # Get or initialize conversation history
    conv_id = request.conversation_id
    if conv_id not in conversation_history:
        conversation_history[conv_id] = []
    
    # Add current message to history
    current_message = Message(
        role="user",
        content=request.message,
        timestamp=datetime.now().isoformat()
    )
    conversation_history[conv_id].append(current_message)
    
    # Combine with provided history
    full_history = request.conversation_history + conversation_history[conv_id]
    
    # Detect scam
    is_scam, confidence, scam_type = detect_scam(request.message, full_history)
    
    # Extract intelligence
    intelligence = extract_intelligence(request.message, full_history)
    
    # Generate agent response
    agent_engaged = is_scam and confidence >= 0.3
    
    if agent_engaged:
        # AI agent takes over
        response_message = generate_agent_response(
            request.message,
            full_history,
            scam_type or "unknown",
            persona_type="elderly"
        )
        reasoning = f"Scam detected with {confidence:.2%} confidence. Agent engaged using elderly persona to extract intelligence."
    else:
        # Not a scam or low confidence
        response_message = "I'm sorry, I didn't quite understand. Could you please clarify?"
        reasoning = f"Low scam confidence ({confidence:.2%}). Awaiting more information."
    
    # Add assistant response to history
    assistant_message = Message(
        role="assistant",
        content=response_message,
        timestamp=datetime.now().isoformat()
    )
    conversation_history[conv_id].append(assistant_message)
    
    # Count turns
    turn_count = len([m for m in conversation_history[conv_id] if m.role == "assistant"])
    
    # Build response
    response = ConversationResponse(
        conversation_id=conv_id,
        is_scam=is_scam,
        confidence=confidence,
        agent_engaged=agent_engaged,
        response_message=response_message,
        turn_count=turn_count,
        extracted_intelligence=intelligence,
        scam_type=scam_type,
        reasoning=reasoning
    )
    
    return response


@app.post("/api/reset/{conversation_id}")
async def reset_conversation(
    conversation_id: str,
    x_api_key: str = Header(..., alias="x-api-key")
):
    """Reset a conversation history"""
    verify_api_key(x_api_key)
    
    if conversation_id in conversation_history:
        del conversation_history[conversation_id]
        return {"status": "success", "message": f"Conversation {conversation_id} reset"}
    
    return {"status": "not_found", "message": f"Conversation {conversation_id} not found"}


@app.get("/api/conversations")
async def list_conversations(x_api_key: str = Header(..., alias="x-api-key")):
    """List all active conversations"""
    verify_api_key(x_api_key)
    
    return {
        "total_conversations": len(conversation_history),
        "conversation_ids": list(conversation_history.keys())
    }


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
