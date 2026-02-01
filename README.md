# Agentic Honey-Pot API - Deployment Guide

## Overview
This is an AI-powered Agentic Honey-Pot system that detects scam messages and autonomously engages scammers to extract intelligence such as bank accounts, UPI IDs, and phishing links.

## Features
✅ Scam detection using pattern matching and ML heuristics
✅ Autonomous AI agent with believable personas
✅ Multi-turn conversation handling
✅ Intelligence extraction (bank accounts, UPI IDs, URLs)
✅ API key authentication
✅ Conversation state management

## Quick Start

### 1. Local Testing

```bash
# Install dependencies
pip install -r requirements.txt

# Run the server
python honeypot_api.py

# In another terminal, test the API
python test_api.py
```

The API will be available at `http://localhost:8000`

### 2. Configure API Key

**IMPORTANT:** Before deployment, change the API key in `honeypot_api.py`:

```python
API_KEY = "your-secret-api-key-here"  # Change this!
```

Generate a secure API key:
```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

### 3. Deployment Options

#### Option A: Railway (Recommended)

1. Create account at https://railway.app
2. Create new project → Deploy from GitHub
3. Or use Railway CLI:
   ```bash
   npm i -g @railway/cli
   railway login
   railway init
   railway up
   ```
4. Set environment variables:
   - `API_KEY`: Your secret API key

#### Option B: Render

1. Create account at https://render.com
2. New → Web Service
3. Connect your GitHub repo
4. Configure:
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `uvicorn honeypot_api:app --host 0.0.0.0 --port $PORT`
5. Add environment variable `API_KEY`

#### Option C: Heroku

1. Create account at https://heroku.com
2. Install Heroku CLI
3. Deploy:
   ```bash
   heroku create your-honeypot-api
   git push heroku main
   heroku config:set API_KEY=your-secret-key
   ```

#### Option D: AWS Lambda (Advanced)

1. Use Mangum adapter for FastAPI
2. Deploy via AWS SAM or Serverless Framework

## API Endpoints

### POST /api/honeypot
Main endpoint for scam detection and agent interaction

**Request:**
```json
{
  "conversation_id": "unique-conv-id",
  "message": "Congratulations! You won a prize...",
  "conversation_history": [],
  "metadata": {}
}
```

**Response:**
```json
{
  "conversation_id": "unique-conv-id",
  "is_scam": true,
  "confidence": 0.85,
  "agent_engaged": true,
  "response_message": "Oh my! Is this really true? How does this work?",
  "turn_count": 1,
  "extracted_intelligence": {
    "bank_accounts": ["123456789012"],
    "upi_ids": ["scammer@paytm"],
    "phone_numbers": [],
    "urls": ["http://phishing-link.com"],
    "other_data": {}
  },
  "scam_type": "lottery_scam",
  "reasoning": "Scam detected with 85% confidence. Agent engaged using elderly persona."
}
```

### GET /health
Health check endpoint

### GET /
Root endpoint - API info

## Testing Your Deployed API

### Using the Hackathon Tester

1. Get your deployed URL (e.g., `https://your-app.railway.app`)
2. In the hackathon tester form:
   - **URL**: `https://your-app.railway.app/api/honeypot`
   - **Header Name**: `x-api-key`
   - **Header Value**: Your API key

### Using cURL

```bash
curl -X POST https://your-app.railway.app/api/honeypot \
  -H "x-api-key: your-secret-api-key-here" \
  -H "Content-Type: application/json" \
  -d '{
    "conversation_id": "test-001",
    "message": "You won Rs 50000! Share your bank account to claim.",
    "conversation_history": []
  }'
```

## How It Works

### 1. Scam Detection
- Pattern matching against known scam indicators
- Keyword analysis
- Confidence scoring (0.0 - 1.0)
- Categorization (lottery_scam, banking_scam, otp_scam, etc.)

### 2. Autonomous Agent
When scam is detected (confidence ≥ 0.3):
- Activates believable persona (elderly person, busy professional, student)
- Engages in multi-turn conversation
- Asks strategic questions to extract intelligence
- Never reveals it detected the scam

### 3. Intelligence Extraction
Automatically extracts:
- Bank account numbers (9-18 digits)
- UPI IDs (email-like format with UPI providers)
- Phone numbers (Indian format)
- URLs and phishing links
- IFSC codes

### 4. Conversation Strategy

**Turn 1**: Express interest and ask for details
**Turn 2**: Show concern but remain engaged
**Turn 3**: Ask for payment/account details
**Turn 4**: Request confirmation of details
**Turn 5+**: Stall with technical difficulties to extract more info

## Customization

### Add More Scam Patterns
Edit `SCAM_PATTERNS` in `honeypot_api.py`:
```python
SCAM_PATTERNS = [
    r"your-regex-pattern",
    # Add more patterns
]
```

### Modify Agent Personas
Edit `PERSONAS` dictionary:
```python
PERSONAS = {
    "your_persona": {
        "name": "Name",
        "age": 50,
        "traits": "personality traits",
        "speech_pattern": "how they communicate"
    }
}
```

### Adjust Detection Threshold
Change confidence threshold in `honeypot_endpoint()`:
```python
agent_engaged = is_scam and confidence >= 0.3  # Adjust this
```

## Evaluation Metrics

Your submission will be evaluated on:

1. **Scam Detection Accuracy**: How well it identifies scams
2. **Engagement Duration**: How long it keeps scammers engaged
3. **Conversation Turns**: Number of back-and-forth exchanges
4. **Intelligence Quality**: Amount and accuracy of extracted data
5. **Response Time**: API latency
6. **Stability**: Uptime and error handling

## Tips for Higher Scores

✅ **Improve Detection**: Add more scam patterns and keywords
✅ **Better Personas**: Create more believable, context-aware responses
✅ **Strategic Engagement**: Ask open-ended questions that encourage detailed answers
✅ **Intelligence Extraction**: Use better regex patterns for phone numbers, accounts, etc.
✅ **Memory**: Reference previous conversation turns
✅ **Never Break Character**: Never reveal you detected the scam

## Advanced: Using Claude API

For even better results, integrate Claude API for dynamic responses:

```python
import anthropic

client = anthropic.Anthropic(api_key="your-anthropic-api-key")

def generate_agent_response_with_claude(message, history, persona):
    prompt = f"""You are {persona['name']}, a {persona['age']} year old {persona['traits']}.
    
    A scammer just sent you this message: "{message}"
    
    Previous conversation:
    {history}
    
    Respond naturally as this persona. Ask questions to get their bank account or UPI ID.
    DO NOT reveal you know it's a scam."""
    
    response = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=1000,
        messages=[{"role": "user", "content": prompt}]
    )
    
    return response.content[0].text
```

## Troubleshooting

**API Key Issues**: Make sure header is `x-api-key` (lowercase with hyphen)

**Deployment Fails**: Check logs for missing dependencies

**Low Confidence Scores**: Add more scam patterns or adjust threshold

**Slow Responses**: Optimize regex patterns or add caching

## Security Notes

⚠️ Never commit your API key to Git
⚠️ Use environment variables in production
⚠️ Rotate API keys regularly
⚠️ Monitor for abuse

## Support

For questions about the hackathon, refer to the official documentation or contact organizers.

## License

This is a hackathon submission for India AI Impact Buildathon.
