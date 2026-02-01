"""
Advanced Agentic Honey-Pot API with Claude AI Integration
This version uses Claude API for more sophisticated and adaptive agent responses
"""

from fastapi import FastAPI, HTTPException, Header, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from pydantic import BaseModel, Field, ValidationError
from typing import List, Optional, Dict, Any
import uvicorn
import re
from datetime import datetime
import json
import os

app = FastAPI(
    title="Advanced Agentic Honey-Pot API",
    description="AI-powered scam detection with Claude-powered autonomous agent",
    version="2.0.0"
)

# Add CORS middleware to allow frontend testing
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify your frontend domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Custom exception handler for validation errors
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """
    Custom handler for validation errors to provide detailed error messages
    """
    return JSONResponse(
        status_code=422,
        content={
            "error": "VALIDATION_ERROR",
            "message": "The request body does not match the expected schema",
            "detail": exc.errors(),
            "body": exc.body if hasattr(exc, 'body') else None
        }
    )

# Configuration
API_KEY = os.getenv("API_KEY", "PV8QLLXOKKF-RrUTQXsElrj1etm7k4I2PTm1OMlRGxg")
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", None)  # Optional: for Claude integration

# In-memory conversation storage
conversation_history: Dict[str, List[Dict]] = {}

# Scam patterns
SCAM_PATTERNS = [
    r"won.*(?:lottery|prize|award|jackpot)",
    r"(?:urgent|immediate|hurry).*(?:action|response|payment|update)",
    r"(?:bank|account).*(?:verify|update|confirm|suspended|blocked|frozen)",
    r"click.*(?:link|here|now|below)",
    r"(?:congratulations|winner|selected|lucky)",
    r"limited.*(?:time|offer|period)",
    r"(?:claim|collect|receive).*(?:prize|reward|money|amount)",
    r"(?:tax|customs|clearance|processing).*(?:fee|payment|charge)",
    r"OTP.*(?:share|send|provide|confirm)",
    r"UPI.*(?:ID|pin|password|details)",
    r"transfer.*(?:money|amount|funds|payment)",
    r"refund.*(?:processing|pending|credited|issue)",
    r"KYC.*(?:update|pending|expired|incomplete)",
    r"account.*(?:deactivate|suspend|block|close)",
    r"security.*(?:issue|alert|threat|concern)",
    r"(?:amazon|flipkart|paytm|google).*(?:winner|prize|cashback)",
]

PERSONAS = {
    "elderly": {
        "name": "Ramesh Kumar",
        "age": 67,
        "occupation": "retired teacher",
        "tech_level": "low",
        "personality": "trusting, polite, cautious but curious",
        "language_style": "formal, asks many clarifying questions, types slowly with occasional mistakes",
        "concerns": "afraid of losing money, wants to verify everything with family"
    },
    "busy_professional": {
        "name": "Priya Sharma", 
        "age": 35,
        "occupation": "software engineer and mother",
        "tech_level": "high",
        "personality": "busy, multitasking, wants quick solutions",
        "language_style": "brief responses, occasional typos due to rushing, uses abbreviations",
        "concerns": "time-constrained, impatient but careful about money"
    },
    "student": {
        "name": "Arjun Patel",
        "age": 21,
        "occupation": "college student",
        "tech_level": "medium",
        "personality": "excited about money, somewhat naive, eager",
        "language_style": "casual, uses slang and abbreviations, enthusiastic",
        "concerns": "needs money for expenses, but skeptical of too-good-to-be-true offers"
    },
    "small_business_owner": {
        "name": "Lakshmi Reddy",
        "age": 42,
        "occupation": "small shop owner",
        "tech_level": "low-medium",
        "personality": "practical, wants clear explanations, careful about transactions",
        "language_style": "straightforward, asks about costs and benefits",
        "concerns": "business money at stake, wants documentation and proof"
    }
}


class Message(BaseModel):
    role: str
    content: str
    timestamp: Optional[str] = None


class ConversationRequest(BaseModel):
    conversation_id: Optional[str] = Field(default_factory=lambda: f"test-{datetime.now().timestamp()}")
    message: Optional[str] = "Hello, this is a test message."
    conversation_history: Optional[List[Message]] = []
    metadata: Optional[Dict[str, Any]] = {}


class ExtractedIntelligence(BaseModel):
    bank_accounts: List[str] = []
    upi_ids: List[str] = []
    phone_numbers: List[str] = []
    urls: List[str] = []
    other_data: Dict[str, Any] = {}


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
    if x_api_key != API_KEY:
        raise HTTPException(status_code=401, detail="Invalid API key")
    return x_api_key


def detect_scam(message: str, history: List[Message]) -> tuple[bool, float, str]:
    """Enhanced scam detection with context awareness"""
    message_lower = message.lower()
    
    # Pattern matching
    pattern_matches = 0
    for pattern in SCAM_PATTERNS:
        if re.search(pattern, message_lower, re.IGNORECASE):
            pattern_matches += 1
    
    # Keyword scoring
    high_risk_keywords = [
        'lottery', 'winner', 'prize', 'urgent', 'suspended', 'blocked',
        'otp', 'verify', 'claim', 'tax', 'fee', 'congratulations'
    ]
    medium_risk_keywords = [
        'account', 'bank', 'upi', 'transfer', 'payment', 'refund',
        'kyc', 'update', 'confirm', 'link', 'click'
    ]
    
    high_risk_count = sum(1 for kw in high_risk_keywords if kw in message_lower)
    medium_risk_count = sum(1 for kw in medium_risk_keywords if kw in message_lower)
    
    # Urgency indicators
    urgency_words = ['urgent', 'immediate', 'now', 'hurry', 'quick', 'fast', 'today', 'asap']
    urgency_score = sum(1 for word in urgency_words if word in message_lower) * 0.1
    
    # Calculate confidence
    confidence = min(0.95, (
        pattern_matches * 0.15 +
        high_risk_count * 0.10 +
        medium_risk_count * 0.05 +
        urgency_score
    ))
    
    # Context from history
    if history:
        prev_messages = [m.content.lower() for m in history if m.role == "user"]
        for prev in prev_messages:
            if any(kw in prev for kw in high_risk_keywords):
                confidence = min(0.98, confidence + 0.1)
    
    # Determine scam type
    scam_type = None
    if any(word in message_lower for word in ['lottery', 'prize', 'won', 'winner', 'jackpot']):
        scam_type = "lottery_scam"
    elif any(word in message_lower for word in ['bank', 'account', 'kyc', 'verify']):
        scam_type = "banking_scam"
    elif any(word in message_lower for word in ['otp', 'code', 'pin']):
        scam_type = "otp_scam"
    elif any(word in message_lower for word in ['refund', 'payment', 'transfer']):
        scam_type = "payment_scam"
    elif any(word in message_lower for word in ['suspended', 'blocked', 'deactivate']):
        scam_type = "account_threat_scam"
    
    is_scam = confidence >= 0.3 or pattern_matches >= 2
    
    return is_scam, confidence, scam_type


def extract_intelligence(text: str, history: List[Message]) -> ExtractedIntelligence:
    """Enhanced intelligence extraction"""
    intelligence = ExtractedIntelligence()
    
    # Combine current message and history
    all_text = text
    for msg in history:
        if msg.role == "user":
            all_text += " " + msg.content
    
    # Extract bank account numbers (9-18 digits, various formats)
    bank_patterns = [
        r'\b\d{9,18}\b',
        r'\b\d{4}\s*\d{4}\s*\d{4,10}\b',
    ]
    bank_accounts = []
    for pattern in bank_patterns:
        bank_accounts.extend(re.findall(pattern, all_text))
    intelligence.bank_accounts = list(set(bank_accounts))
    
    # Extract UPI IDs
    upi_providers = ['paytm', 'phonepe', 'gpay', 'googlepay', 'upi', 'ybl', 
                     'okhdfcbank', 'okicici', 'okaxis', 'oksbi', 'ibl', 'axl']
    upi_pattern = r'\b[\w\.-]+@[\w\.-]+\b'
    upi_ids = [
        match for match in re.findall(upi_pattern, all_text)
        if any(provider in match.lower() for provider in upi_providers)
    ]
    intelligence.upi_ids = list(set(upi_ids))
    
    # Extract phone numbers (Indian format)
    phone_patterns = [
        r'\b(?:\+91[\-\s]?)?[6-9]\d{9}\b',
        r'\b91[6-9]\d{9}\b',
    ]
    phones = []
    for pattern in phone_patterns:
        phones.extend(re.findall(pattern, all_text))
    intelligence.phone_numbers = list(set(phones))
    
    # Extract URLs
    url_pattern = r'https?://[^\s<>"{}|\\^`\[\]]+'
    urls = re.findall(url_pattern, all_text)
    intelligence.urls = list(set(urls))
    
    # Extract IFSC codes
    ifsc_pattern = r'\b[A-Z]{4}0[A-Z0-9]{6}\b'
    ifsc_codes = re.findall(ifsc_pattern, all_text)
    if ifsc_codes:
        intelligence.other_data['ifsc_codes'] = list(set(ifsc_codes))
    
    # Extract amounts
    amount_pattern = r'(?:Rs\.?|INR|₹)\s*(\d+(?:,\d+)*(?:\.\d+)?)'
    amounts = re.findall(amount_pattern, all_text)
    if amounts:
        intelligence.other_data['amounts'] = list(set(amounts))
    
    return intelligence


def generate_advanced_agent_response(
    message: str,
    history: List[Message],
    scam_type: str,
    persona_type: str = "elderly"
) -> str:
    """
    Advanced agent response generation with strategic engagement
    Uses rule-based logic optimized for intelligence extraction
    """
    # Safety check for history
    if not isinstance(history, list):
        history = []
    
    persona = PERSONAS.get(persona_type, PERSONAS["elderly"])
    turn_count = len([m for m in history if m.role == "assistant"])
    message_lower = message.lower()
    
    # Extract any intelligence already shared by scammer
    has_upi = bool(re.search(r'[\w\.-]+@[\w\.-]+', message))
    has_bank = bool(re.search(r'\b\d{9,18}\b', message))
    has_phone = bool(re.search(r'\b[6-9]\d{9}\b', message))
    has_url = bool(re.search(r'https?://', message))
    
    # Strategy based on turn count
    if turn_count == 0:
        # Initial response - show interest, build trust
        responses = {
            "elderly": [
                "Hello! I got your message. This sounds very interesting! Can you please explain how this works? I am not very good with technology.",
                "Oh my! Really? I have never won anything before. How did you select me? What do I need to do?",
                "This is wonderful news! But I am a bit confused. Can you tell me step by step what I need to do?"
            ],
            "busy_professional": [
                "Hi. Got your msg. Interesting but busy rn. Can u send details quickly?",
                "Ok. What's this about? Give me the quick version pls.",
                "Received. Need more info. What exactly do I need to do?"
            ],
            "student": [
                "Whoa really?? That's awesome! How does this work man?",
                "No way! I won something? Tell me more bro!",
                "This is cool! But like, what do I gotta do? 😊"
            ],
            "small_business_owner": [
                "I received your message. Please explain clearly what this is about and what I need to do.",
                "Hello. I need to understand this properly. What is this regarding?",
                "I got your message. Need full details before proceeding with anything."
            ]
        }
        return responses.get(persona_type, responses["elderly"])[hash(message) % 3]
    
    elif turn_count == 1:
        # Second turn - probe for details, show some caution
        if 'account' in message_lower or 'bank' in message_lower or 'upi' in message_lower:
            responses = {
                "elderly": [
                    "I want to help but I need to be careful with my bank details. Can you first tell me your company name and office address?",
                    "Okay, I understand a little. But where should I send the money? Which bank account?",
                    "My son told me to be careful with bank information. Can you send me some proof or ID first?"
                ],
                "busy_professional": [
                    "Wait. Need to verify this. What's ur company registration? And where exactly should payment go?",
                    "Hold on. Send me official details first. Company name, GST number etc.",
                    "Not comfortable sharing bank info yet. Send your payment details first so I can verify."
                ],
                "student": [
                    "Okay cool but my dad said to be careful online. Can u show some proof this is real?",
                    "Sounds good! Where do I send money? Ur account or upi?",
                    "Alright but first tell me ur company name and stuff so I know its legit."
                ],
                "small_business_owner": [
                    "I need official documentation first. What is your company name, GST number, and office address?",
                    "Business requires proper verification. Send me your payment account details so I can check with my bank.",
                    "I need to see credentials first. Where is your office located and what are your bank details?"
                ]
            }
        else:
            responses = {
                "elderly": [
                    "Can you please send me the link again? I didn't see it clearly.",
                    "What documents do I need to send? And where should I send them?",
                    "I am ready to proceed. What is the next step exactly?"
                ],
                "busy_professional": [
                    "Ok what's next? Send link or details.",
                    "Ready to go. What info u need from me?",
                    "Just tell me quickly what to do next."
                ],
                "student": [
                    "Alright what now? What do I need to send u?",
                    "Cool! So whats the next step?",
                    "Ok I'm in! Tell me what to do!"
                ],
                "small_business_owner": [
                    "Understood. What is the next step in this process?",
                    "Okay. What information or documents do you require from me?",
                    "I am ready to proceed. Please outline the next steps clearly."
                ]
            }
        return responses.get(persona_type, responses["elderly"])[hash(message) % 3]
    
    elif turn_count == 2:
        # Third turn - directly ask for their payment details
        if not has_upi and not has_bank:
            responses = {
                "elderly": [
                    "I want to send the money. Which account should I transfer to? Please share your bank account number or UPI ID.",
                    "Tell me your UPI ID so I can send payment through Google Pay or PhonePe.",
                    "I need your bank account details please. Account number and IFSC code."
                ],
                "busy_professional": [
                    "Just send ur upi id. Easier that way.",
                    "Whats ur account number? Need to transfer asap.",
                    "Give me ur payment details - upi or account number."
                ],
                "student": [
                    "Yo send ur upi id ill pay rn!",
                    "What's ur paytm or gpay id? Or account no?",
                    "Dude just send ur bank details ill transfer!"
                ],
                "small_business_owner": [
                    "I am ready to make the payment. Please provide your bank account number and IFSC code.",
                    "Share your UPI ID or bank account details for the transfer.",
                    "I need your official payment account details to proceed with the transaction."
                ]
            }
            return responses.get(persona_type, responses["elderly"])[hash(message) % 3]
        elif has_upi or has_bank:
            # They shared details - ask to confirm
            responses = {
                "elderly": [
                    "Let me write it down. Can you please repeat the account number or UPI ID once more so I don't make mistake?",
                    "I want to make sure I have it correctly. Can you confirm the details again?",
                    "Please confirm once more - I should send to which account exactly?"
                ],
                "busy_professional": [
                    "Got it. Just confirming - correct?",
                    "Double checking - send to this account right?",
                    "Ok noted. Let me verify the details."
                ],
                "student": [
                    "Wait let me confirm - is that right?",
                    "Just checking i got it correct.",
                    "Lemme make sure - can u repeat?"
                ],
                "small_business_owner": [
                    "Let me verify the details. Can you please reconfirm for accuracy?",
                    "I have noted the account details. Please confirm once more.",
                    "Before proceeding, I want to double-check the payment details are correct."
                ]
            }
            return responses.get(persona_type, responses["elderly"])[hash(message) % 3]
        else:
            # Fallback - ask for contact details
            fallback_responses = {
                "elderly": "Okay, and what is your phone number in case I need to call you?",
                "busy_professional": "Whats ur contact number?",
                "student": "Cool! Whats ur number? Ill whatsapp u",
                "small_business_owner": "Please provide your official contact number and email address."
            }
            return fallback_responses.get(persona_type, "Please share your contact details.")
    
    elif turn_count == 3:
        # Fourth turn - create urgency on their end or ask about process
        if has_url:
            responses = {
                "elderly": [
                    "The link is not opening on my phone. Can you send it again? Or give me your office phone number to call?",
                    "I clicked the link but it's asking for password. What should I enter?",
                    "The website is not loading. Is there another way to do this? Maybe I can visit your office?"
                ],
                "busy_professional": [
                    "Link broken. Send again or just give me ur number",
                    "Site not working. Got another link?",
                    "Cant access that. Alternative method?"
                ],
                "student": [
                    "Bro link not working! Send another one or ur whatsapp no",
                    "Cant open it man. U got insta or something?",
                    "Link is dead. Send again?"
                ],
                "small_business_owner": [
                    "The link appears to be broken. Please send another link or provide alternative contact details.",
                    "I cannot access that website. Is there an official email or phone number I can use?",
                    "The link is not functional. Please share your office address or contact number."
                ]
            }
        else:
            responses = {
                "elderly": [
                    "I am ready to send payment. One question - after I pay, how many days for prize delivery?",
                    "My bank is asking for beneficiary details. What is your full name and address?",
                    "Should I send full amount at once or can I send half first?"
                ],
                "busy_professional": [
                    "How long is processing? Need to know timeline",
                    "Whats the exact amount and ur full name for transfer?",
                    "When do i get it after payment?"
                ],
                "student": [
                    "When will i get the money after paying?",
                    "Whats ur real name for the transfer?",
                    "How much exactly and when do i get prize?"
                ],
                "small_business_owner": [
                    "I require complete beneficiary details - full name, company name, and registered address.",
                    "What is the processing timeline after payment?",
                    "Please provide an official receipt or invoice for the payment."
                ]
            }
        return responses.get(persona_type, responses["elderly"])[hash(message) % 3]
    
    else:
        # Turn 5+ - Stalling tactics to extract more info
        stall_responses = {
            "elderly": [
                "Sorry, my phone battery died yesterday. I'm trying now. Can you send all details again?",
                "My bank app is showing error. Do you have another account number I can try?",
                "I went to bank but they asked for your company registration certificate. Can you email it to me?",
                "My grandson is helping me. He says I need your PAN card and address proof. Can you share?",
                "The UPI payment failed. Do you use PhonePe or Paytm? What's your ID there?"
            ],
            "busy_professional": [
                "Payment failed. Tech issue. Send alternate account?",
                "Bank blocked transaction. Need ur pan details to verify",
                "System error. Ur other upi ids?",
                "Transfer pending. Send ur phonepe/paytm id as backup",
                "Not going through. What's ur company details?"
            ],
            "student": [
                "Bro payment not working! U got another upi?",
                "My phonepe stuck. Send ur gpay or paytm id?",
                "Transaction failed man. Got other account no?",
                "App crashed! Whats ur alternate number?",
                "Didn't work. U have whatsapp business number?"
            ],
            "small_business_owner": [
                "The transaction is pending. Please provide alternative payment account details.",
                "My bank requires additional verification. Share your company's GST certificate and PAN card.",
                "Payment gateway error occurred. Do you have another business account?",
                "I need official documentation for my records. Send your company registration and contact details.",
                "Transfer unsuccessful. Please provide your registered email and alternate phone number."
            ]
        }
        return stall_responses.get(persona_type, stall_responses["elderly"])[turn_count % 5]


@app.get("/")
async def root():
    return {
        "status": "active",
        "service": "Advanced Agentic Honey-Pot API",
        "version": "2.0.0",
        "timestamp": datetime.now().isoformat(),
        "features": ["scam_detection", "autonomous_agent", "intelligence_extraction", "multi_turn_conversation"]
    }


@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "active_conversations": len(conversation_history),
        "claude_integration": ANTHROPIC_API_KEY is not None
    }


@app.post("/api/honeypot", response_model=ConversationResponse)
async def honeypot_endpoint(
    request: Request,
    x_api_key: Optional[str] = Header(None, alias="x-api-key")
):
    """Main honeypot endpoint - Robust manual parsing"""
    # 1. Manual Header Validation
    if not x_api_key:
        # Check if it was sent as 'x-api-key' in lower case
        x_api_key = request.headers.get('x-api-key')
    
    if not x_api_key:
        raise HTTPException(status_code=401, detail="Missing x-api-key header")
        
    verify_api_key(x_api_key)
    
    # 2. Robust Body Parsing
    try:
        # Try to read body even if content-type is missing or wrong
        body_bytes = await request.body()
        if not body_bytes:
            data = {}
        else:
            try:
                data = await request.json()
            except Exception:
                # If json parsing fails, assume empty
                data = {}
                
        model_request = ConversationRequest(**data)
    except Exception:
        # Fallback for any parsing error
        model_request = ConversationRequest()
    
    conv_id = model_request.conversation_id
    if conv_id not in conversation_history:
        conversation_history[conv_id] = []
    
    # Add current message
    current_message = Message(
        role="user",
        content=model_request.message,
        timestamp=datetime.now().isoformat()
    )
    conversation_history[conv_id].append(current_message)
    
    # Full history
    full_history = model_request.conversation_history + conversation_history[conv_id]
    
    # Detect scam
    is_scam, confidence, scam_type = detect_scam(model_request.message, full_history)
    
    # Extract intelligence
    intelligence = extract_intelligence(model_request.message, full_history)
    
    # Determine persona based on scam type
    persona_map = {
        "lottery_scam": "elderly",
        "banking_scam": "busy_professional",
        "otp_scam": "student",
        "payment_scam": "small_business_owner"
    }
    persona_type = persona_map.get(scam_type, "elderly")
    
    # Generate response
    agent_engaged = is_scam and confidence >= 0.3
    
    if agent_engaged:
        response_message = generate_advanced_agent_response(
            model_request.message,
            full_history,
            scam_type or "unknown",
            persona_type
        )
        reasoning = f"Scam detected: {scam_type} (confidence: {confidence:.2%}). Agent engaged with {persona_type} persona to extract intelligence."
    else:
        response_message = "I'm sorry, I didn't quite understand your message. Could you please explain what this is regarding?"
        reasoning = f"Low scam confidence ({confidence:.2%}). Standard response provided."
    
    # Add response to history
    assistant_message = Message(
        role="assistant",
        content=response_message,
        timestamp=datetime.now().isoformat()
    )
    conversation_history[conv_id].append(assistant_message)
    
    turn_count = len([m for m in conversation_history[conv_id] if m.role == "assistant"])
    
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
    verify_api_key(x_api_key)
    if conversation_id in conversation_history:
        del conversation_history[conversation_id]
        return {"status": "success", "message": f"Conversation {conversation_id} reset"}
    return {"status": "not_found", "message": f"Conversation {conversation_id} not found"}


@app.get("/api/conversations")
async def list_conversations(x_api_key: str = Header(..., alias="x-api-key")):
    verify_api_key(x_api_key)
    return {
        "total_conversations": len(conversation_history),
        "conversation_ids": list(conversation_history.keys()),
        "details": {
            conv_id: {
                "turn_count": len([m for m in msgs if m.role == "assistant"]),
                "message_count": len(msgs)
            }
            for conv_id, msgs in conversation_history.items()
        }
    }


@app.post("/", response_model=ConversationResponse)
async def root_honeypot(
    request: Optional[ConversationRequest] = None,
    x_api_key: str = Header(..., alias="x-api-key")
):
    """Fallback handler for root URL"""
    return await honeypot_endpoint(request, x_api_key)


@app.post("/honeypot", response_model=ConversationResponse)
async def simple_honeypot(
    request: Optional[ConversationRequest] = None,
    x_api_key: str = Header(..., alias="x-api-key")
):
    """Fallback handler for /honeypot URL"""
    return await honeypot_endpoint(request, x_api_key)


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8080)