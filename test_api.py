import requests
import json

BASE_URL = "http://localhost:8000"

def test_health():
    response = requests.get(f"{BASE_URL}/health")
    print(f"Health: {response.status_code} - {response.json()}")
    return response.status_code == 200

def test_analyze():
    data = {
        "ticket_id": "TKT-001",
        "complaint": "I sent 5000 taka to a wrong number at 2pm today",
        "language": "en",
        "channel": "in_app_chat",
        "user_type": "customer",
        "campaign_context": "boishakh_bonanza_day_1",
        "transaction_history": [
            {
                "transaction_id": "TXN-9101",
                "timestamp": "2026-04-14T14:08:22Z",
                "type": "transfer",
                "amount": 5000,
                "counterparty": "+8801719876543",
                "status": "completed"
            }
        ]
    }
    
    response = requests.post(
        f"{BASE_URL}/analyze-ticket",
        json=data,
        headers={"Content-Type": "application/json"}
    )
    
    print(f"Analyze: {response.status_code}")
    if response.status_code == 200:
        print(json.dumps(response.json(), indent=2))
    else:
        print(f"Error: {response.text}")
    
    return response.status_code == 200

def test_wrong_transfer():
    data = {
        "ticket_id": "TKT-002",
        "complaint": "I sent money to the wrong person",
        "transaction_history": [
            {
                "transaction_id": "TXN-9102",
                "timestamp": "2026-04-14T14:10:22Z",
                "type": "transfer",
                "amount": 3000,
                "counterparty": "+8801719876544",
                "status": "completed"
            }
        ]
    }
    
    response = requests.post(
        f"{BASE_URL}/analyze-ticket",
        json=data,
        headers={"Content-Type": "application/json"}
    )
    
    print(f"Wrong Transfer Test: {response.status_code}")
    if response.status_code == 200:
        result = response.json()
        print(f"Verdict: {result['evidence_verdict']}")
        print(f"Case Type: {result['case_type']}")
        print(f"Department: {result['department']}")
    
    return response.status_code == 200

if __name__ == "__main__":
    print("Testing QueueStorm API...")
    print("-" * 50)
    
    tests_passed = 0
    tests_total = 3
    
    if test_health():
        print("✅ Health check passed")
        tests_passed += 1
    else:
        print("❌ Health check failed")
    
    print("-" * 50)
    
    if test_analyze():
        print("✅ Analyze test passed")
        tests_passed += 1
    else:
        print("❌ Analyze test failed")
    
    print("-" * 50)
    
    if test_wrong_transfer():
        print("✅ Wrong transfer test passed")
        tests_passed += 1
    else:
        print("❌ Wrong transfer test failed")
    
    print("=" * 50)
    print(f"Tests Passed: {tests_passed}/{tests_total}")
    if tests_passed == tests_total:
        print("🎉 All tests passed! Your service is working correctly.")
    else:
        print("⚠️ Some tests failed. Please check your service.")
