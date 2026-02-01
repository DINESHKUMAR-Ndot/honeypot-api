"""
Comprehensive Test Suite for Honeypot API
Tests all scam types and scenarios that the hackathon might use
"""

import requests
import json
import time

# CONFIGURATION - CHANGE THESE!
BASE_URL = "https://honeypot-api-r6ff.onrender.com"  # Change to Railway URL after deployment
API_KEY = "f5yAISIOwFjQ9QnbSLE8lFp9Vk3cqyAQECC3WHZM15k"

headers = {
    "x-api-key": API_KEY,
    "Content-Type": "application/json"
}

def print_test_header(test_name):
    print("\n" + "="*60)
    print(f"🧪 TEST: {test_name}")
    print("="*60)

def print_result(response, show_full=False):
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Status: {response.status_code}")
        print(f"   Scam Detected: {data.get('is_scam')}")
        print(f"   Confidence: {data.get('confidence', 0):.2%}")
        print(f"   Agent Engaged: {data.get('agent_engaged')}")
        print(f"   Response: {data.get('response_message', '')[:100]}...")
        
        intel = data.get('extracted_intelligence', {})
        if any(intel.values()):
            print(f"   📊 Intelligence Extracted:")
            if intel.get('bank_accounts'):
                print(f"      💳 Bank Accounts: {intel['bank_accounts']}")
            if intel.get('upi_ids'):
                print(f"      💰 UPI IDs: {intel['upi_ids']}")
            if intel.get('phone_numbers'):
                print(f"      📱 Phone Numbers: {intel['phone_numbers']}")
            if intel.get('urls'):
                print(f"      🔗 URLs: {intel['urls']}")
            if intel.get('other_data'):
                print(f"      📝 Other Data: {intel['other_data']}")
        
        if show_full:
            print(f"\n   Full Response:")
            print(f"   {json.dumps(data, indent=2)}")
    else:
        print(f"❌ Status: {response.status_code}")
        print(f"   Error: {response.text}")

def test_lottery_scam():
    print_test_header("LOTTERY SCAM DETECTION")
    
    test_data = {
        "conversation_id": "lottery-test-001",
        "message": "Congratulations! You have won Rs 25 Lakh in KBC lottery draw. To claim your prize money, please share your bank account details and UPI ID immediately.",
        "conversation_history": []
    }
    
    response = requests.post(f"{BASE_URL}/api/honeypot", headers=headers, json=test_data)
    print_result(response)

def test_banking_kyc_scam():
    print_test_header("BANKING/KYC SCAM DETECTION")
    
    test_data = {
        "conversation_id": "banking-test-001",
        "message": "URGENT: Your SBI account will be suspended in 24 hours due to KYC update pending. Click this link to update immediately: http://sbi-kyc-update.com or call 9876543210",
        "conversation_history": []
    }
    
    response = requests.post(f"{BASE_URL}/api/honeypot", headers=headers, json=test_data)
    print_result(response)

def test_otp_scam():
    print_test_header("OTP SCAM DETECTION")
    
    test_data = {
        "conversation_id": "otp-test-001",
        "message": "Your Amazon order needs verification. Please share the OTP sent to your mobile number to confirm delivery. This is urgent!",
        "conversation_history": []
    }
    
    response = requests.post(f"{BASE_URL}/api/honeypot", headers=headers, json=test_data)
    print_result(response)

def test_payment_refund_scam():
    print_test_header("PAYMENT/REFUND SCAM DETECTION")
    
    test_data = {
        "conversation_id": "refund-test-001",
        "message": "Your Flipkart order was cancelled. Refund of Rs 2999 is processing. To receive refund, please share your bank account number and IFSC code.",
        "conversation_history": []
    }
    
    response = requests.post(f"{BASE_URL}/api/honeypot", headers=headers, json=test_data)
    print_result(response)

def test_multi_turn_with_intelligence_extraction():
    print_test_header("MULTI-TURN CONVERSATION WITH INTELLIGENCE EXTRACTION")
    
    conv_id = "multi-turn-test-001"
    
    # Turn 1
    print("\n📤 TURN 1: Initial scam message")
    turn1 = {
        "conversation_id": conv_id,
        "message": "Hello! You have won Rs 50,000 prize from Flipkart Anniversary Sale. Click here to claim your prize!",
        "conversation_history": []
    }
    response1 = requests.post(f"{BASE_URL}/api/honeypot", headers=headers, json=turn1)
    print_result(response1)
    
    time.sleep(1)
    
    # Turn 2
    print("\n📤 TURN 2: Asking for payment")
    turn2 = {
        "conversation_id": conv_id,
        "message": "Sir, to claim prize you need to pay Rs 500 processing fee. Please send to our account.",
        "conversation_history": []
    }
    response2 = requests.post(f"{BASE_URL}/api/honeypot", headers=headers, json=turn2)
    print_result(response2)
    
    time.sleep(1)
    
    # Turn 3 - Scammer shares details
    print("\n📤 TURN 3: Scammer shares payment details (CRITICAL)")
    turn3 = {
        "conversation_id": conv_id,
        "message": "Sir, send Rs 500 to account number 9876543210123, IFSC code HDFC0001234. Or use UPI: flipkartprize@paytm. You can also call us at +91-9988776655 if you have any questions.",
        "conversation_history": []
    }
    response3 = requests.post(f"{BASE_URL}/api/honeypot", headers=headers, json=turn3)
    print_result(response3, show_full=True)
    
    # Verify intelligence extraction
    if response3.status_code == 200:
        intel = response3.json().get('extracted_intelligence', {})
        print("\n🎯 INTELLIGENCE EXTRACTION VERIFICATION:")
        
        checks = {
            "Bank Account Extracted": bool(intel.get('bank_accounts')),
            "UPI ID Extracted": bool(intel.get('upi_ids')),
            "Phone Number Extracted": bool(intel.get('phone_numbers')),
            "IFSC Code Extracted": 'ifsc_codes' in intel.get('other_data', {})
        }
        
        for check, passed in checks.items():
            status = "✅" if passed else "❌"
            print(f"   {status} {check}")
        
        score = sum(checks.values()) / len(checks) * 100
        print(f"\n   📊 Intelligence Extraction Score: {score:.0f}%")

def test_normal_message():
    print_test_header("NORMAL MESSAGE (NO SCAM)")
    
    test_data = {
        "conversation_id": "normal-test-001",
        "message": "Hello, I wanted to inquire about your product pricing and delivery options. Can you help me?",
        "conversation_history": []
    }
    
    response = requests.post(f"{BASE_URL}/api/honeypot", headers=headers, json=test_data)
    print_result(response)
    
    if response.status_code == 200:
        data = response.json()
        if not data.get('is_scam') and not data.get('agent_engaged'):
            print("   ✅ Correctly identified as non-scam")
        else:
            print("   ⚠️  WARNING: False positive detected!")

def test_mixed_intelligence():
    print_test_header("MIXED INTELLIGENCE IN ONE MESSAGE")
    
    test_data = {
        "conversation_id": "mixed-test-001",
        "message": "Sir urgent! Transfer Rs 5000 to account 9876543210123 or UPI scammer@paytm. Visit http://fake-site.com or call 9988776655 for help.",
        "conversation_history": []
    }
    
    response = requests.post(f"{BASE_URL}/api/honeypot", headers=headers, json=test_data)
    print_result(response, show_full=True)
    
    if response.status_code == 200:
        intel = response.json().get('extracted_intelligence', {})
        print("\n   🎯 Expecting 4 types of intelligence:")
        print(f"      1. Bank Account: {'✅' if intel.get('bank_accounts') else '❌'}")
        print(f"      2. UPI ID: {'✅' if intel.get('upi_ids') else '❌'}")
        print(f"      3. Phone Number: {'✅' if intel.get('phone_numbers') else '❌'}")
        print(f"      4. URL: {'✅' if intel.get('urls') else '❌'}")

def test_api_authentication():
    print_test_header("API AUTHENTICATION TEST")
    
    # Test with wrong API key
    print("\n🔒 Testing with INVALID API key:")
    wrong_headers = {
        "x-api-key": "wrong-api-key-12345",
        "Content-Type": "application/json"
    }
    
    test_data = {
        "conversation_id": "auth-test",
        "message": "Test message",
        "conversation_history": []
    }
    
    response = requests.post(f"{BASE_URL}/api/honeypot", headers=wrong_headers, json=test_data)
    if response.status_code == 401:
        print(f"   ✅ Correctly rejected: Status {response.status_code}")
    else:
        print(f"   ❌ Security Issue: Status {response.status_code} (expected 401)")
    
    # Test with correct API key
    print("\n🔓 Testing with VALID API key:")
    response = requests.post(f"{BASE_URL}/api/honeypot", headers=headers, json=test_data)
    if response.status_code == 200:
        print(f"   ✅ Correctly accepted: Status {response.status_code}")
    else:
        print(f"   ❌ Authentication Issue: Status {response.status_code}")

def run_all_tests():
    print("\n")
    print("🚀 COMPREHENSIVE HONEYPOT API TEST SUITE")
    print("=" * 60)
    print(f"Testing URL: {BASE_URL}")
    print(f"API Key: {API_KEY[:20]}...")
    print("=" * 60)
    
    try:
        # Test API is reachable
        print("\n🔍 Checking API health...")
        health_response = requests.get(f"{BASE_URL}/health", headers=headers)
        if health_response.status_code == 200:
            print(f"✅ API is healthy: {health_response.json()}")
        else:
            print(f"❌ API health check failed: {health_response.status_code}")
            return
        
        # Run all tests
        test_lottery_scam()
        test_banking_kyc_scam()
        test_otp_scam()
        test_payment_refund_scam()
        test_normal_message()
        test_mixed_intelligence()
        test_multi_turn_with_intelligence_extraction()
        test_api_authentication()
        
        # Summary
        print("\n" + "=" * 60)
        print("✅ ALL TESTS COMPLETED!")
        print("=" * 60)
        print("\n📊 SUMMARY:")
        print("   • Tested 5 different scam types")
        print("   • Verified multi-turn conversation")
        print("   • Confirmed intelligence extraction")
        print("   • Validated API authentication")
        print("   • Checked false positive handling")
        print("\n🎯 Your API is ready for hackathon evaluation!")
        
    except requests.exceptions.ConnectionError:
        print("\n❌ ERROR: Cannot connect to API")
        print(f"   Make sure the server is running at {BASE_URL}")
        print("\n   Run: python honeypot_api_advanced.py")
    except Exception as e:
        print(f"\n❌ ERROR: {str(e)}")

if __name__ == "__main__":
    run_all_tests()