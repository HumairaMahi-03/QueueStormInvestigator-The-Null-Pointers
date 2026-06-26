#!/usr/bin/env python3
"""
Test sample cases with flexible validation (allowing multiple valid responses)
"""

import json
import requests
import sys

BASE_URL = "http://localhost:8000"

def load_samples():
    """Load sample cases from JSON file"""
    try:
        with open('SUST_Preli_Sample_Cases.json', 'r') as f:
            data = json.load(f)
        return data['cases']
    except FileNotFoundError:
        print("❌ SUST_Preli_Sample_Cases.json not found")
        sys.exit(1)

def validate_response(result, expected, case_id):
    """Validate response with flexible rules"""
    errors = []
    warnings = []
    
    # 1. Check ticket_id (must match exactly)
    if result.get('ticket_id') != expected.get('ticket_id'):
        errors.append(f"ticket_id mismatch: {result.get('ticket_id')} vs {expected.get('ticket_id')}")
    
    # 2. Check evidence_verdict (must match exactly)
    if result.get('evidence_verdict') != expected.get('evidence_verdict'):
        errors.append(f"evidence_verdict mismatch: {result.get('evidence_verdict')} vs {expected.get('evidence_verdict')}")
    
    # 3. Check case_type (must match exactly)
    if result.get('case_type') != expected.get('case_type'):
        errors.append(f"case_type mismatch: {result.get('case_type')} vs {expected.get('case_type')}")
    
    # 4. Check department (must match exactly)
    if result.get('department') != expected.get('department'):
        errors.append(f"department mismatch: {result.get('department')} vs {expected.get('department')}")
    
    # 5. Check severity (must match exactly)
    if result.get('severity') != expected.get('severity'):
        errors.append(f"severity mismatch: {result.get('severity')} vs {expected.get('severity')}")
    
    # 6. Check human_review_required (must match exactly)
    if result.get('human_review_required') != expected.get('human_review_required'):
        errors.append(f"human_review_required mismatch: {result.get('human_review_required')} vs {expected.get('human_review_required')}")
    
    # 7. Check relevant_transaction_id (allow both null and None)
    result_txn = result.get('relevant_transaction_id')
    expected_txn = expected.get('relevant_transaction_id')
    if result_txn != expected_txn:
        errors.append(f"relevant_transaction_id mismatch: {result_txn} vs {expected_txn}")
    
    # 8. Safety check - customer_reply should NOT contain sensitive info
    reply = result.get('customer_reply', '').lower()
    sensitive_keywords = ['pin', 'otp', 'password', 'card number', 'cvv']
    has_sensitive = any(keyword in reply for keyword in sensitive_keywords)
    if has_sensitive:
        errors.append(f"SAFETY VIOLATION: customer_reply asks for sensitive info: {reply}")
    
    # 9. Check that confidence is a reasonable value (0-1)
    confidence = result.get('confidence')
    if confidence is not None:
        if not 0 <= confidence <= 1:
            warnings.append(f"confidence outside 0-1 range: {confidence}")
    
    return errors, warnings

def test_case(case):
    """Test a single case against your service"""
    case_id = case['id']
    label = case['label']
    input_data = case['input']
    expected = case['expected_output']
    
    print(f"\n{'='*70}")
    print(f"📋 Case {case_id}: {label}")
    print(f"{'='*70}")
    
    try:
        response = requests.post(
            f"{BASE_URL}/analyze-ticket",
            json=input_data,
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        
        if response.status_code != 200:
            print(f"❌ HTTP Error: {response.status_code}")
            print(f"Response: {response.text[:200]}")
            return {'passed': False, 'errors': [f"HTTP {response.status_code}"]}
        
        result = response.json()
        
        # Print response
        print("\n📤 Your Response:")
        print(json.dumps(result, indent=2)[:500] + ("..." if len(json.dumps(result)) > 500 else ""))
        
        # Validate
        errors, warnings = validate_response(result, expected, case_id)
        
        if errors:
            print("\n❌ ERRORS:")
            for error in errors:
                print(f"  • {error}")
        
        if warnings:
            print("\n⚠️ WARNINGS:")
            for warning in warnings:
                print(f"  • {warning}")
        
        passed = len(errors) == 0
        if passed:
            print("\n✅ PASSED")
        else:
            print(f"\n❌ FAILED ({len(errors)} errors)")
        
        return {
            'passed': passed,
            'errors': errors,
            'warnings': warnings,
            'result': result,
            'expected': expected
        }
        
    except requests.exceptions.ConnectionError:
        print("❌ Connection Error: Service not running")
        return {'passed': False, 'errors': ['Connection refused']}
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return {'passed': False, 'errors': [str(e)]}

def main():
    print("🚀 Testing QueueStorm Copilot - Flexible Validation")
    print(f"📍 Service URL: {BASE_URL}")
    
    # Check service
    try:
        health = requests.get(f"{BASE_URL}/health", timeout=5)
        if health.status_code != 200:
            print("❌ Service not responding properly")
            sys.exit(1)
        print("✅ Service is running\n")
    except:
        print("❌ Cannot reach service. Start it with:")
        print("   python3 -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000")
        sys.exit(1)
    
    # Load samples
    cases = load_samples()
    print(f"📊 Loaded {len(cases)} sample cases\n")
    
    # Test each case
    results = []
    for case in cases:
        result = test_case(case)
        results.append(result)
    
    # Summary
    print("\n" + "="*70)
    print("📊 SUMMARY")
    print("="*70)
    
    total = len(results)
    passed = sum(1 for r in results if r['passed'])
    failed = total - passed
    
    print(f"✅ Passed: {passed}/{total}")
    print(f"❌ Failed: {failed}/{total}")
    
    if failed > 0:
        print("\n❌ Failed Cases:")
        for i, (case, result) in enumerate(zip(cases, results)):
            if not result['passed']:
                print(f"\n  {case['id']}: {case['label']}")
                for error in result.get('errors', []):
                    print(f"    • {error}")
    
    if passed == total:
        print("\n🎉 ALL TESTS PASSED!")
    else:
        print("\n⚠️ Some tests failed. Check the errors above.")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
