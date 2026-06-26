#!/usr/bin/env python3
"""
Test the enhanced classifier with various inputs
"""

import sys
sys.path.append('.')
from app.classifier import (
    CaseType, Severity, Department, EvidenceVerdict,
    classify_case
)

test_cases = [
    {
        "name": "Banglish wrong transfer",
        "complaint": "ami vul number e 1000 taka send korechi",
        "expected": CaseType.wrong_transfer
    },
    {
        "name": "Bangla failed payment",
        "complaint": "টাকা কেটেছে কিন্তু লেনদেন হয়নি",
        "expected": CaseType.payment_failed
    },
    {
        "name": "Bangla phishing",
        "complaint": "ওটিপি চাইছে ফোন করে",
        "expected": CaseType.phishing_or_social_engineering
    },
    {
        "name": "Mixed language refund",
        "complaint": "আমার 500 taka refund চাই",
        "expected": CaseType.refund_request
    }
]

print("Testing Enhanced Classifier...")
print("="*60)

for test in test_cases:
    case_type, _, _, _, _, _ = classify_case(
        complaint=test["complaint"],
        user_type="customer",
        relevant_txn=None,
        evidence_verdict=EvidenceVerdict.insufficient_data
    )
    
    status = "✅" if case_type == test["expected"] else "❌"
    print(f"{status} {test['name']}")
    print(f"   Complaint: {test['complaint']}")
    print(f"   Got: {case_type.value}, Expected: {test['expected'].value}")
    print()

