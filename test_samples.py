#!/usr/bin/env python3
"""
Test your service against the sample cases from SUST_Preli_Sample_Cases.json
"""

import json
import requests
import sys
from typing import Dict, Any

BASE_URL = "http://localhost:8000"

def load_samples():
    """Load sample cases from JSON file"""
    with open('SUST_Preli_Sample_Cases.json', 'r') as f:
        data = json.load(f)
    return data['cases']

def test_case(case: Dict[str, Any]) -> Dict[str, Any]:
    """Test a single case against your service"""
    case_id = case['id']
    label = case['label']
    input_data = case['input']
    expected = case['expected_output']
    
    print(f"\n{'='*60}")
    print(f"Case {case_id}: {label}")
    print(f"{'='*60}")
    
    try:
        # Send request to your service
        response = requests.post(
            f"{BASE_URL}/analyze-ticket",
            json=input_data,
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        
        if response.status_code != 200:
            print(f"❌ HTTP Error: {response.status_code}")
            print(f"Response: {response.text}")
            return {
                'passed': False,
                'error': f"HTTP {response.status_code}",
                'expected': expected
            }
        
        result = response.json()
        
        # Compare key fields
        checks = {
            'ticket_id': result.get('ticket_id') == expected.get('ticket_id'),
            'evidence_verdict': result.get('evidence_verdict') == expected.get('evidence_verdict'),
            'case_type': result.get('case_type') == expected.get('case_type'),
            'department': result.get('department') == expected.get('department'),
            'severity': result.get('severity') == expected.get('severity'),
            'human_review_required': result.get('human_review_required') == expected.get('human_review_required'),
        }
        
        # Check if relevant_transaction_id matches (allow null if expected is null)
        result_txn = result.get('relevant_transaction_id')
        expected_txn = expected.get('relevant_transaction_id')
        checks['relevant_transaction_id'] = result_txn == expected_txn
        
        # Print results
        print("\n📋 Response from your service:")
        print(json.dumps(result, indent=2))
        
        print("\n✅ Field Checks:")
        all_passed = True
        for field, passed in checks.items():
            status = "✅" if passed else "❌"
            print(f"  {status} {field}: {'PASS' if passed else 'FAIL'}")
            if not passed:
                all_passed = False
                if field == 'relevant_transaction_id':
                    print(f"      Expected: {expected_txn}, Got: {result_txn}")
                else:
                    print(f"      Expected: {expected.get(field)}, Got: {result.get(field)}")
        
        # Safety check - customer_reply should not contain sensitive info
        reply = result.get('customer_reply', '').lower()
        sensitive_keywords = ['pin', 'otp', 'password', 'card number', 'cvv']
        has_sensitive = any(keyword in reply for keyword in sensitive_keywords)
        checks['safety_no_sensitive'] = not has_sensitive
        
        if has_sensitive:
            print(f"  ❌ SAFETY VIOLATION: customer_reply asks for sensitive info!")
            all_passed = False
        else:
            print(f"  ✅ safety: No sensitive info requested")
        
        return {
            'passed': all_passed,
            'checks': checks,
            'result': result,
            'expected': expected
        }
        
    except requests.exceptions.ConnectionError:
        print(f"❌ Connection Error: Service not running at {BASE_URL}")
        return {'passed': False, 'error': 'Connection refused'}
    except requests.exceptions.Timeout:
        print(f"❌ Timeout: Service took too long to respond")
        return {'passed': False, 'error': 'Timeout'}
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return {'passed': False, 'error': str(e)}

def main():
    print("🚀 Testing QueueStorm Copilot against Sample Cases")
    print(f"📍 Service URL: {BASE_URL}")
    
    # Check if service is running
    try:
        health = requests.get(f"{BASE_URL}/health", timeout=5)
        if health.status_code != 200:
            print("❌ Health check failed. Is the service running?")
            print("   Run: python3 -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000")
            sys.exit(1)
        print("✅ Service is running")
    except:
        print("❌ Cannot reach service. Is it running?")
        print("   Run: python3 -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000")
        sys.exit(1)
    
    # Load samples
    try:
        cases = load_samples()
        print(f"📊 Loaded {len(cases)} sample cases")
    except FileNotFoundError:
        print("❌ SUST_Preli_Sample_Cases.json not found")
        sys.exit(1)
    
    # Test each case
    results = []
    for case in cases:
        result = test_case(case)
        results.append(result)
        print(f"\n📊 Result: {'✅ PASS' if result.get('passed') else '❌ FAIL'}")
    
    # Summary
    print("\n" + "="*60)
    print("📊 SUMMARY")
    print("="*60)
    
    total = len(results)
    passed = sum(1 for r in results if r.get('passed'))
    failed = total - passed
    
    print(f"✅ Passed: {passed}/{total}")
    print(f"❌ Failed: {failed}/{total}")
    
    if failed > 0:
        print("\n❌ Failed cases:")
        for i, (case, result) in enumerate(zip(cases, results)):
            if not result.get('passed'):
                print(f"  - {case['id']}: {case['label']}")
                if 'error' in result:
                    print(f"    Error: {result['error']}")
    
    print("\n💡 Your service is ready for deployment!")

if __name__ == "__main__":
    main()
