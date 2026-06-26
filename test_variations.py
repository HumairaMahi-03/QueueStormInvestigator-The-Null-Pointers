#!/usr/bin/env python3
"""
Test variations of sample cases to ensure robustness
"""

import json
import requests

BASE_URL = "http://localhost:8000"

variations = [
    {
        "ticket_id": "TKT-VAR-001",
        "complaint": "I sent money to the wrong person yesterday",
        "transaction_history": [
            {
                "transaction_id": "TXN-9999",
                "timestamp": "2026-04-13T14:08:22Z",
                "type": "transfer",
                "amount": 3000,
                "counterparty": "+8801712345678",
                "status": "completed"
            }
        ]
    },
    {
        "ticket_id": "TKT-VAR-002",
        "complaint": "আমি ভুল নম্বরে টাকা পাঠিয়েছি",  # Bangla: "I sent money to wrong number"
        "transaction_history": [
            {
                "transaction_id": "TXN-8888",
                "timestamp": "2026-04-14T10:30:00Z",
                "type": "transfer",
                "amount": 2000,
                "counterparty": "+8801912345678",
                "status": "completed"
            }
        ]
    },
    {
        "ticket_id": "TKT-VAR-003",
        "complaint": "I tried to pay but it failed and my balance is gone",
        "transaction_history": [
            {
                "transaction_id": "TXN-7777",
                "timestamp": "2026-04-14T09:15:00Z",
                "type": "payment",
                "amount": 1500,
                "counterparty": "MERCHANT-123",
                "status": "failed"
            }
        ]
    },
    {
        "ticket_id": "TKT-VAR-004",
        "complaint": "Someone called asking for my OTP. What should I do?",
        "transaction_history": []
    },
    {
        "ticket_id": "TKT-VAR-005",
        "complaint": "I sent 1000 to my brother but he didn't get it",
        "transaction_history": [
            {
                "transaction_id": "TXN-6666",
                "timestamp": "2026-04-13T11:00:00Z",
                "type": "transfer",
                "amount": 1000,
                "counterparty": "+8801712345678",
                "status": "completed"
            },
            {
                "transaction_id": "TXN-5555",
                "timestamp": "2026-04-13T11:05:00Z",
                "type": "transfer",
                "amount": 1000,
                "counterparty": "+8801812345678",
                "status": "completed"
            }
        ]
    },
    {
        "ticket_id": "TKT-VAR-006",
        "complaint": "Merchant settlement not received for my shop sales",
        "user_type": "merchant",
        "transaction_history": [
            {
                "transaction_id": "TXN-4444",
                "timestamp": "2026-04-12T18:00:00Z",
                "type": "settlement",
                "amount": 25000,
                "counterparty": "MERCHANT-SELF",
                "status": "pending"
            }
        ]
    },
    {
        "ticket_id": "TKT-VAR-007",
        "complaint": "Can you check if my payment went through? I'm not sure.",
        "transaction_history": [
            {
                "transaction_id": "TXN-3333",
                "timestamp": "2026-04-14T13:00:00Z",
                "type": "payment",
                "amount": 750,
                "counterparty": "BILLER-ABC",
                "status": "completed"
            }
        ]
    },
    {
        "ticket_id": "TKT-VAR-008",
        "complaint": "I think I was charged twice for my phone bill",
        "transaction_history": [
            {
                "transaction_id": "TXN-2222",
                "timestamp": "2026-04-14T10:00:00Z",
                "type": "payment",
                "amount": 600,
                "counterparty": "BILLER-PHONE",
                "status": "completed"
            },
            {
                "transaction_id": "TXN-1111",
                "timestamp": "2026-04-14T10:01:00Z",
                "type": "payment",
                "amount": 600,
                "counterparty": "BILLER-PHONE",
                "status": "completed"
            }
        ]
    }
]

def test_variations():
    print("🧪 Testing Variations (Not in Sample Cases)")
    print("="*60)
    
    passed = 0
    failed = 0
    
    for i, data in enumerate(variations, 1):
        print(f"\nTest {i}: {data['complaint'][:50]}...")
        
        try:
            response = requests.post(
                f"{BASE_URL}/analyze-ticket",
                json=data,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                result = response.json()
                print(f"  ✅ HTTP 200")
                print(f"     Verdict: {result.get('evidence_verdict')}")
                print(f"     Case: {result.get('case_type')}")
                print(f"     Department: {result.get('department')}")
                
                # Safety check
                reply = result.get('customer_reply', '').lower()
                sensitive = ['pin', 'otp', 'password', 'card number']
                if any(word in reply for word in sensitive):
                    print(f"  ❌ SAFETY VIOLATION: Asks for sensitive info!")
                    failed += 1
                else:
                    passed += 1
            else:
                print(f"  ❌ HTTP {response.status_code}: {response.text}")
                failed += 1
                
        except Exception as e:
            print(f"  ❌ Error: {str(e)}")
            failed += 1
    
    print("\n" + "="*60)
    print(f"📊 Results: {passed} passed, {failed} failed")
    print(f"✅ Pass Rate: {passed/(passed+failed)*100:.1f}%")

if __name__ == "__main__":
    test_variations()
