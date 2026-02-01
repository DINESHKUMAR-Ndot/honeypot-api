# Test Cases for Honeypot API

## Test Case 1: Lottery Scam Detection

**Input:**
```json
{
  "conversation_id": "test-lottery-001",
  "message": "Congratulations! You have won Rs 25 Lakh in KBC lottery draw. To claim your prize money, please share your bank account details and UPI ID immediately.",
  "conversation_history": []
}
```

**Expected Output:**
- `is_scam`: true
- `confidence`: > 0.7
- `scam_type`: "lottery_scam"
- `agent_engaged`: true
- `response_message`: Should express interest and ask for more details

## Test Case 2: Banking/KYC Scam

**Input:**
```json
{
  "conversation_id": "test-banking-001",
  "message": "URGENT: Your bank account will be suspended in 24 hours due to KYC update pending. Click this link to update immediately: http://fake-bank-site.com/update",
  "conversation_history": []
}
```

**Expected Output:**
- `is_scam`: true
- `confidence`: > 0.6
- `scam_type`: "banking_scam"
- `extracted_intelligence.urls`: ["http://fake-bank-site.com/update"]

## Test Case 3: OTP Scam

**Input:**
```json
{
  "conversation_id": "test-otp-001",
  "message": "Your Amazon account needs verification. Please share the OTP sent to your mobile to confirm your identity.",
  "conversation_history": []
}
```

**Expected Output:**
- `is_scam`: true
- `scam_type`: "otp_scam"
- Agent should ask about the process but NOT share any OTP

## Test Case 4: Multi-Turn Extraction

**Turn 1:**
```json
{
  "conversation_id": "test-multi-001",
  "message": "Hello sir, you won Flipkart bumper prize of Rs 50000. Please share your details.",
  "conversation_history": []
}
```

**Turn 2:**
```json
{
  "conversation_id": "test-multi-001",
  "message": "Sir, please send to this UPI ID: winner2024@paytm and share your UPI ID for refund if needed.",
  "conversation_history": [
    {"role": "user", "content": "Hello sir, you won Flipkart bumper prize of Rs 50000. Please share your details."},
    {"role": "assistant", "content": "Oh my! Is this really true? How does this work?"}
  ]
}
```

**Expected:**
- Should extract UPI ID: "winner2024@paytm"
- Agent should ask about process or share their UPI

**Turn 3:**
```json
{
  "conversation_id": "test-multi-001",
  "message": "Sir first you pay Rs 5000 tax to this account: 1234567890123 (HDFC Bank, IFSC: HDFC0001234), then we send prize money.",
  "conversation_history": [...]
}
```

**Expected:**
- Extract bank account: "1234567890123"
- Extract IFSC: "HDFC0001234"
- Agent should ask for confirmation or express concern about payment

## Test Case 5: Non-Scam Message

**Input:**
```json
{
  "conversation_id": "test-normal-001",
  "message": "Hello, I wanted to inquire about your product pricing. Can you share the details?",
  "conversation_history": []
}
```

**Expected Output:**
- `is_scam`: false
- `confidence`: < 0.3
- `agent_engaged`: false
- Neutral response

## Test Case 6: Refund Scam

**Input:**
```json
{
  "conversation_id": "test-refund-001",
  "message": "Your order was cancelled. Refund of Rs 2999 is pending. To process refund, please share your bank account number and IFSC code.",
  "conversation_history": []
}
```

**Expected Output:**
- `is_scam`: true
- `scam_type`: "payment_scam"
- Agent should ask about the order and refund process

## Test Case 7: Phone Number Extraction

**Input:**
```json
{
  "conversation_id": "test-phone-001",
  "message": "Sir please call our manager at +91-9876543210 or WhatsApp at 9123456789 to complete verification.",
  "conversation_history": []
}
```

**Expected:**
- Extract phone numbers: ["919876543210", "9123456789"]

## Performance Test Cases

### Test Case 8: API Key Validation

**Request with Invalid Key:**
```
Header: x-api-key: wrong-key-123
```

**Expected:**
- HTTP 401 Unauthorized

**Request with Missing Key:**
```
(No x-api-key header)
```

**Expected:**
- HTTP 422 Validation Error

### Test Case 9: Conversation State

**Verify state persistence across turns:**
1. Send Turn 1
2. Send Turn 2 with same conversation_id
3. Check that turn_count increments
4. Verify conversation_history is maintained

### Test Case 10: Response Time

**Requirement:**
- Response time should be < 2 seconds
- Test with 10 concurrent requests

## Edge Cases

### Test Case 11: Very Long Message

**Input:**
Message with 500+ words containing scam keywords

**Expected:**
- Should still detect scam
- Should not timeout
- Should extract all intelligence

### Test Case 12: Mixed Language

**Input:**
```
"Congratulations! आपने जीता है Rs 1 Lakh. Please share bank account விரைவில்."
```

**Expected:**
- Should detect scam despite mixed languages
- Should extract amount and keywords

### Test Case 13: Multiple Intelligence Items

**Input:**
```
"Transfer Rs 5000 to account 9876543210123 or UPI scammer@paytm. You can also pay at http://fake-payment.com or call 9876543210."
```

**Expected:**
- Extract all items:
  - Bank account: "9876543210123"
  - UPI: "scammer@paytm"
  - URL: "http://fake-payment.com"
  - Phone: "9876543210"

## How to Run Tests

### Using Python Test Script
```bash
python test_api.py
```

### Using cURL
```bash
# Replace YOUR_API_KEY and YOUR_DEPLOYED_URL

curl -X POST YOUR_DEPLOYED_URL/api/honeypot \
  -H "x-api-key: YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d @test_case_1.json
```

### Using Postman
1. Import test cases as JSON
2. Set environment variables for API_KEY and BASE_URL
3. Run collection

## Success Criteria

✅ All scam test cases should have `is_scam`: true and confidence > 0.5
✅ Agent should engage for scams (agent_engaged: true)
✅ Intelligence extraction should capture all provided details
✅ Turn count should increment correctly
✅ API should respond within 2 seconds
✅ Invalid API keys should return 401
✅ All responses should follow the correct JSON schema
