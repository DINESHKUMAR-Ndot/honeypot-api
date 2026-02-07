
import requests
import json
import time

# YOUR LIVE URL
API_URL = "https://honeypot-api-r6ff.onrender.com/api/honeypot"
API_KEY = "f5yAISIOwFjQ9QnbSLE8lFp9Vk3cqyAQECC3WHZM15k"

# Session ID
session_id = f"manual-test-{int(time.time())}"
history = []

print("="*50)
print("🤖 AGENTIC HONEYPOT - INTERACTIVE TESTER")
print("="*50)
print(f"Target: {API_URL}")
print("Type a message (e.g., 'Your account is blocked') and press Enter.")
print("Type 'exit' to quit.")
print("-" * 50)

while True:
    try:
        user_input = input("\n😈 SCAMMER (You): ")
        if user_input.lower() in ["exit", "quit"]:
            break
            
        # Construct Official Payload
        payload = {
            "sessionId": session_id,
            "message": {
                "sender": "scammer",
                "text": user_input,
                "timestamp": int(time.time() * 1000)
            },
            "conversationHistory": history,
            "metadata": {"channel": "CLI", "language": "en"}
        }

        headers = {
            "Content-Type": "application/json",
            "x-api-key": API_KEY
        }

        print("... sending ...")
        
        response = requests.post(API_URL, json=payload, headers=headers)
        
        if response.status_code == 200:
            data = response.json()
            reply = data.get("reply", "NO REPLY")
            status = data.get("status", "unknown")
            
            print(f"🛡️  AGENT (Bot): {reply}")
            
            # Add to history for next turn (to simulate multi-turn)
            history.append({"sender": "scammer", "text": user_input})
            history.append({"sender": "user", "text": reply})
            
        else:
            print(f"🔴 ERROR: Status {response.status_code}")
            print(response.text)
            
    except Exception as e:
        print(f"❌ Error: {e}")
