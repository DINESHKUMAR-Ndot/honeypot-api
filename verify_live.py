
import requests
import json
import time

# YOUR LIVE URL
API_URL = "https://honeypot-api-r6ff.onrender.com/api/honeypot"
API_KEY = "f5yAISIOwFjQ9QnbSLE8lFp9Vk3cqyAQECC3WHZM15k"

# 1. SIMULATE A SCAM MESSAGE (Official Schema)
payload = {
    "sessionId": "test-session-verification-001",
    "message": {
        "sender": "scammer",
        "text": "Your HDFC bank account will be blocked today! Urgent KYC update required. Click here: http://fake-bank-verify.com",
        "timestamp": int(time.time() * 1000)
    },
    "conversationHistory": [],
    "metadata": {
        "channel": "SMS",
        "language": "English"
    }
}

headers = {
    "Content-Type": "application/json",
    "x-api-key": API_KEY
}

print(f"🔵 Sending Test Request to: {API_URL}")
print(f"🔵 Payload: {json.dumps(payload, indent=2)}")
print("-" * 50)

try:
    response = requests.post(API_URL, json=payload, headers=headers)
    
    print(f"🟢 Status Code: {response.status_code}")
    
    try:
        data = response.json()
        print(f"🟢 Response Body: {json.dumps(data, indent=2)}")
        
        # VERIFICATION LOGIC
        if data.get("status") == "success" and data.get("reply"):
            print("\n✅ SUCCESS! The API accepted the request and the Agent replied.")
            print(f"🗣️ Agent Reply: \"{data['reply']}\"")
            print("(This proves your API is working perfectly)")
        else:
            print("\n⚠️ WARNING: Response format looks unexpected.")
            
    except Exception as e:
        print(f"🔴 Could not parse JSON response: {response.text}")

except Exception as e:
    print(f"🔴 Connection Failed: {e}")
