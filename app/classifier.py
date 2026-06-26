"""
app/classifier.py - Final fixed version with explicit human_review logic
"""

import re
from typing import List, Optional, Tuple

from app.models import (
    TransactionHistoryEntry,
    EvidenceVerdict,
    CaseType,
    Severity,
    Department,
)
from app.config import settings

# Enhanced keyword lists with Bangla support
PHISHING_KEYWORDS = [
    "otp", "pin", "password", "verification code", "asked me for my",
    "called me", "claimed to be from", "scam", "fraudulent call", 
    "suspicious call", "security code", "verify your account",
    "account will be blocked", "account will be suspended",
    "urgent action required", "click this link", "phishing",
    "ওটিপি", "পিন", "পাসওয়ার্ড", "ভেরিফিকেশন কোড",
    "আমাকে ফোন করেছে", "স্ক্যাম", "জালিয়াতি", "সন্দেহজনক কল",
    "otp chai", "pin lagbe", "password bolun",
]

DUPLICATE_KEYWORDS = [
    "twice", "duplicate", "charged again", "double charge",
    "two times", "double payment", "charged twice", "double deducted",
    "more than once", "multiple charges", "two transactions",
    "দুবার", "ডুপ্লিকেট", "দুইবার চার্জ", "ডাবল চার্জ",
    "duplicate payment", "double charge", "two bar",
]

WRONG_TRANSFER_KEYWORDS = [
    "wrong number", "wrong recipient", "wrong person", 
    "wrong account", "sent to wrong", "wrong destination",
    "mistakenly sent", "accidentally sent", "not the right person",
    "wrongly sent", "incorrect number", "wrong address",
    "ভুল নম্বর", "ভুল ব্যক্তি", "ভুল অ্যাকাউন্ট",
    "ভুল জায়গায়", "ভুল করে পাঠিয়েছি",
    "vul number", "vul person", "wrong number e",
    "vul account e", "vul jaygay",
]

FAILED_KEYWORDS = [
    "failed", "did not go through", "didn't go through", 
    "deducted but", "money deducted", "balance deducted",
    "no confirmation", "transaction failed", "payment failed",
    "not completed", "unsuccessful", "declined",
    "money gone", "funds deducted", "charged but failed",
    "ব্যর্থ", "টাকা কেটেছে", "ব্যালেন্স কাটা",
    "লেনদেন ব্যর্থ", "পেমেন্ট ব্যর্থ", 
    "failed hoyeche", "kete geche", "balance kete geche",
    "transction fail", "payment fail",
]

REFUND_KEYWORDS = [
    "refund", "return my money", "want my money back",
    "give my money back", "money back", "reverse the transaction",
    "refund request", "refund my payment",
    "টাকা ফেরত", "ফেরত চাই", "টাকা ফেরত চাই",
    "আমার টাকা ফেরত", "টাকা ফেরত দেওয়ার",
    "refund", "taka ferot", "ferot chai",
    "taka ferot chai", "money ferot",
]

SETTLEMENT_KEYWORDS = [
    "settlement", "merchant payout", "haven't received payment from",
    "settlement delayed", "payout not received", "payment not settled",
    "merchant payment", "sales settlement",
    "সেটেলমেন্ট", "মার্চেন্ট পেমেন্ট", "পেমেন্ট পাইনি",
    "settlement hoyni", "payment pai ni",
]

AGENT_CASHIN_KEYWORDS = [
    "agent", "cash in", "cash-in", "deposit through",
    "agent deposit", "cash deposit", "agent cash",
    "deposited with agent", "agent transaction",
    "এজেন্ট", "ক্যাশ ইন", "এজেন্টের মাধ্যমে জমা",
    "agent", "cash in", "deposit korechi",
]

def _any_keyword(text: str, keywords: List[str]) -> bool:
    lower = text.lower()
    return any(kw in lower for kw in keywords)

def _is_likely_wrong_transfer(complaint: str) -> bool:
    if _any_keyword(complaint, WRONG_TRANSFER_KEYWORDS):
        return True
    if re.search(r'sent\s+(?:it|money|amount)\s+to', complaint, re.IGNORECASE):
        return True
    if re.search(r'পাঠিয়েছি|পাঠাইছি|send করেছি', complaint):
        return True
    if "brother" in complaint.lower() or "sister" in complaint.lower() or "friend" in complaint.lower():
        return True
    return False

def _is_likely_failed_payment(complaint: str, relevant_txn: Optional[TransactionHistoryEntry]) -> bool:
    if _any_keyword(complaint, FAILED_KEYWORDS):
        return True
    if relevant_txn and relevant_txn.status.value == "failed":
        return True
    if re.search(r'balance.*deducted|deducted.*balance|kete.*geche', complaint, re.IGNORECASE):
        return True
    return False

def classify_case(
    complaint: str,
    user_type: Optional[str],
    relevant_txn: Optional[TransactionHistoryEntry],
    evidence_verdict: EvidenceVerdict,
) -> Tuple[CaseType, Severity, Department, bool, float, List[str]]:

    reason_codes: List[str] = []
    
    # Determine case type
    if _any_keyword(complaint, PHISHING_KEYWORDS):
        case_type = CaseType.phishing_or_social_engineering
        department = Department.fraud_risk
        reason_codes.append("phishing_signal")

    elif user_type == "agent" or _any_keyword(complaint, AGENT_CASHIN_KEYWORDS):
        case_type = CaseType.agent_cash_in_issue
        department = Department.agent_operations
        reason_codes.append("agent_cashin_signal")

    elif _any_keyword(complaint, DUPLICATE_KEYWORDS):
        case_type = CaseType.duplicate_payment
        department = Department.payments_ops
        reason_codes.append("duplicate_signal")

    elif _is_likely_wrong_transfer(complaint):
        case_type = CaseType.wrong_transfer
        department = Department.dispute_resolution
        reason_codes.append("wrong_transfer_signal")

    elif _is_likely_failed_payment(complaint, relevant_txn):
        case_type = CaseType.payment_failed
        department = Department.payments_ops
        reason_codes.append("payment_failed_signal")

    elif user_type == "merchant" or _any_keyword(complaint, SETTLEMENT_KEYWORDS):
        case_type = CaseType.merchant_settlement_delay
        department = Department.merchant_operations
        reason_codes.append("settlement_signal")

    elif _any_keyword(complaint, REFUND_KEYWORDS):
        case_type = CaseType.refund_request
        department = Department.customer_support
        reason_codes.append("refund_request_signal")

    else:
        case_type = CaseType.other
        department = Department.customer_support
        reason_codes.append("no_specific_signal")

    if relevant_txn is not None:
        reason_codes.append("transaction_match")
        reason_codes.append(f"txn_{relevant_txn.transaction_id}")
    else:
        reason_codes.append("no_transaction_match")

    high_value = relevant_txn is not None and relevant_txn.amount >= settings.HIGH_VALUE_THRESHOLD

    # Severity logic
    if case_type == CaseType.phishing_or_social_engineering:
        severity = Severity.critical
    elif case_type == CaseType.wrong_transfer and evidence_verdict == EvidenceVerdict.inconsistent:
        severity = Severity.medium
    elif case_type == CaseType.wrong_transfer and relevant_txn is None:
        severity = Severity.medium
    elif case_type == CaseType.wrong_transfer:
        severity = Severity.high
    elif case_type == CaseType.payment_failed:
        if relevant_txn and relevant_txn.amount >= 1000:
            severity = Severity.high
        else:
            severity = Severity.medium
    elif case_type == CaseType.agent_cash_in_issue:
        severity = Severity.high
    elif case_type == CaseType.duplicate_payment:
        severity = Severity.high
    elif case_type == CaseType.refund_request:
        severity = Severity.low
    elif case_type == CaseType.other and evidence_verdict == EvidenceVerdict.insufficient_data:
        severity = Severity.low
    elif evidence_verdict == EvidenceVerdict.inconsistent:
        severity = Severity.medium
    else:
        severity = Severity.medium

    # ============================================================
    # HUMAN REVIEW LOGIC - EXPLICIT AND CLEAR
    # ============================================================
    
    # Start with False
    human_review_required = False
    
    # Case type based decisions (highest priority)
    if case_type == CaseType.phishing_or_social_engineering:
        human_review_required = True
    elif case_type == CaseType.agent_cash_in_issue:
        human_review_required = True
    elif case_type == CaseType.duplicate_payment:
        human_review_required = True
    elif case_type == CaseType.wrong_transfer:
        # Wrong transfer with a transaction found = needs review
        # Wrong transfer without a transaction = no review needed
        if relevant_txn is not None:
            human_review_required = True
        else:
            human_review_required = False
    
    # Evidence based decisions
    elif evidence_verdict == EvidenceVerdict.inconsistent:
        human_review_required = True
    
    # Value based decisions
    elif high_value:
        human_review_required = True
    
    # ============================================================
    # CASES THAT NEVER NEED HUMAN REVIEW (OVERRIDE)
    # ============================================================
    
    # SAMPLE-09: Merchant settlements NEVER need human review
    if case_type == CaseType.merchant_settlement_delay:
        human_review_required = False
    
    # Vague complaints with insufficient data
    if case_type == CaseType.other and evidence_verdict == EvidenceVerdict.insufficient_data:
        human_review_required = False

    # Confidence scoring
    if evidence_verdict == EvidenceVerdict.consistent and relevant_txn is not None:
        confidence = 0.9
    elif evidence_verdict == EvidenceVerdict.inconsistent:
        confidence = 0.75
    else:
        confidence = 0.4

    return case_type, severity, department, human_review_required, confidence, reason_codes
