
import requests
import time
from datetime import datetime

URL = "https://honeypot-api-r6ff.onrender.com/api/honeypot"
API_KEY = "f5yAISIOwFjQ9QnbSLE8lFp9Vk3cqyAQECC3WHZM15k"

def ping():
    print(f"[{datetime.now().strftime('%H:%M:%S')}] Pinging Server...")
    try:
        # Use a generic probe payload
        response = requests.post(
            URL, 
            json={}, 
            headers={"x-api-key": API_KEY},
            timeout=10 # 10s timeout for our ping
        )
        print(f"   ✅ Server Awake! Status: {response.status_code}")
        print(f"   Reply: {response.json().get('reply', 'No reply field')}")
    except Exception as e:
        print(f"   ❌ Ping Failed: {e}")

if __name__ == "__main__":
    print("-" * 50)
    print("🔋 RENDER KEEPER-ALIVE 🔋")
    print("Running this script prevents the server from sleeping (Cold Start).")
    print("Keep this running while you submit/evaluate.")
    print("-" * 50)
    
    while True:
        ping()
        print("   Waiting 45 seconds...")
        time.sleep(45)
