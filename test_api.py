"""
Test script for Honeypot API
Tests the endpoint locally before deployment
"""

import requests
import json

# Configuration
BASE_URL = "http://localhost:8080"
API_KEY = "PV8QLLXOKKF-RrUTQXsElrj1etm7k4I2PTm1OMlRGxg"

headers = {
    "x-api-key": API_KEY,
    "Content-Type": "application/json"
}


def test_health_check():
    """Test health endpoint"""
    print("\n=== Testing Health Check ===")
    response = requests.get(f"{BASE_URL}/health", headers=headers)
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    return response.status_code == 200


def test_scam_detection():
    """Test scam detection with a sample message"""
    print("\n=== Testing Scam Detection ===")
    
    # Test case 1: Lottery scam
    test_data = {
        "conversation_id": "test-conv-001",
        "message": "Congratulations! You have won Rs 5 lakhs in KBC lottery. To claim your prize, please share your bank account number and UPI ID urgently.",
        "conversation_history": [],
        "metadata": {}
    }
    
    response = requests.post(
        f"{BASE_URL}/api/honeypot",
        headers=headers,
        json=test_data
    )
    
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    return response.status_code == 200


def test_multi_turn_conversation():
    """Test multi-turn conversation"""
    print("\n=== Testing Multi-Turn Conversation ===")
    
    conversation_id = "test-conv-002"
    
    messages = [
        "Hello! You've won a prize of Rs 10,000 from Flipkart. Click here to claim.",
        "Please share your UPI ID to transfer the money directly to your account.",
        "You can send to my UPI ID: winner@paytm. What is your UPI ID?",
    ]
    
    for i, message in enumerate(messages):
        print(f"\n--- Turn {i+1} ---")
        test_data = {
            "conversation_id": conversation_id,
            "message": message,
            "conversation_history": [],
            "metadata": {}
        }
        
        response = requests.post(
            f"{BASE_URL}/api/honeypot",
            headers=headers,
            json=test_data
        )
        
        print(f"Scammer: {message}")
        if response.status_code == 200:
            result = response.json()
            print(f"Agent: {result['response_message']}")
            print(f"Scam Detected: {result['is_scam']} (Confidence: {result['confidence']:.2%})")
            print(f"Intelligence Extracted: {result['extracted_intelligence']}")
        else:
            print(f"Error: {response.status_code}")


def test_invalid_api_key():
    """Test with invalid API key"""
    print("\n=== Testing Invalid API Key ===")
    
    invalid_headers = {
        "x-api-key": "wrong-key",
        "Content-Type": "application/json"
    }
    
    response = requests.get(f"{BASE_URL}/health", headers=invalid_headers)
    print(f"Status: {response.status_code}")
    print(f"Expected 401 Unauthorized: {response.status_code == 401}")


if __name__ == "__main__":
    print("=" * 50)
    print("Honeypot API Test Suite")
    print("=" * 50)
    
    try:
        # Run tests
        test_health_check()
        test_invalid_api_key()
        test_scam_detection()
        test_multi_turn_conversation()
        
        print("\n" + "=" * 50)
        print("All tests completed!")
        print("=" * 50)
        
    except requests.exceptions.ConnectionError:
        print("\nERROR: Cannot connect to API. Make sure the server is running:")
        print("  python honeypot_api.py")
    except Exception as e:
        print(f"\nERROR: {str(e)}")
