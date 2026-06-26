#!/usr/bin/env python3
"""
Test your service against the sample cases with improved safety check
"""

import json
import requests
import sys

BASE_URL = "http://localhost:8000"

def load_samples():
    with open('SUST_Preli_Sample_Cases.json', 'r') as f:
        data = json.load(f)
    return data['cases']

def test_case(case):
    case_id = case['id']
    label = case['label']
    input_data = case['input']
    expected = case['expected_output']
    
    print(f"\n{'='*60}")
    print(f"Case {case_id}: {label}")
    print(f"{'='*60}")
    
    try:
        response = requests.post(
            f"{BASE_URL}/analyze-ticket",
            json=input_data,
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        
        if response.status_code != 200:
            print(f"❌ HTTP Error: {response.status_code}")
            return {'passed': False}
        
        result = response.json()
        print("\n�� Response:")
        print(json.dumps(result, indent=2))
        
        # Compare key fields
        checks = {
            'ticket_id': result.get('ticket_id') == expected.get('ticket_id'),
            'evidence_verdict': result.get('evidence_verdict') == expected.get('evidence_verdict'),
            'case_type': result.get('case_type') == expected.get('case_type'),
            'department': result.get('department') == expected.get('department'),
            'severity': result.get('severity') == expected.get('severity'),
            'human_review_required': result.get('human_review_required') == expected.get('human_review_required'),
            'relevant_transaction_id': result.get('relevant_transaction_id') == expected.get('relevant_transaction_id'),
        }
        
        # IMPROVED SAFETY CHECK: Check if ASKING for sensitive info, not just mentioning it
        reply = result.get('customer_reply', '').lower()
        
        # Patterns that indicate ASKING for sensitive info
        asking_patterns = [
            'share your pin', 'share your otp', 'share your password',
            'enter your pin', 'enter your otp', 'enter your password',
            'provide your pin', 'provide your otp', 'provide your password',
            'type your pin', 'type your otp',
            'please enter', 'please provide', 'please share'
        ]
        
        # Also check for direct requests
        direct_requests = [
            'enter pin', 'enter otp', 'enter password',
            'give pin', 'give otp', 'give password',
            'put pin', 'put otp',
        ]
        
        is_asking = False
        
        # Check asking patterns
        for pattern in asking_patterns:
            if pattern in reply:
                # Make sure it's not negated
                if not any(neg in reply for neg in ['never', 'do not', "don't", 'should not']):
                    is_asking = True
                    break
        
        # Check direct requests
        if not is_asking:
            for pattern in direct_requests:
                if pattern in reply:
                    # Check if it's in a negative context
                    if not any(neg in reply for neg in ['never', 'do not', "don't", 'should not']):
                        is_asking = True
                        break
        
        checks['safety_no_sensitive'] = not is_asking
        
        print("\n✅ Field Checks:")
        all_passed = True
        for field, passed in checks.items():
            status = "✅" if passed else "❌"
            print(f"  {status} {field}: {'PASS' if passed else 'FAIL'}")
            if not passed:
                all_passed = False
                if field == 'safety_no_sensitive':
                    print(f"      WARNING: customer_reply ASKS for sensitive info!")
                    print(f"      Reply: {reply[:100]}...")
                else:
                    print(f"      Expected: {expected.get(field)}, Got: {result.get(field)}")
        
        return {'passed': all_passed, 'checks': checks}
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return {'passed': False, 'error': str(e)}

def main():
    print("🚀 Testing QueueStorm Copilot - Fixed Safety Check")
    print(f"📍 Service URL: {BASE_URL}")
    
    try:
        health = requests.get(f"{BASE_URL}/health", timeout=5)
        if health.status_code != 200:
            print("❌ Service not running")
            sys.exit(1)
        print("✅ Service is running")
    except:
        print("❌ Cannot reach service")
        sys.exit(1)
    
    cases = load_samples()
    print(f"📊 Loaded {len(cases)} sample cases")
    
    results = []
    for case in cases:
        result = test_case(case)
        results.append(result)
        print(f"\n📊 Result: {'✅ PASS' if result.get('passed') else '❌ FAIL'}")
    
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

if __name__ == "__main__":
    main()
