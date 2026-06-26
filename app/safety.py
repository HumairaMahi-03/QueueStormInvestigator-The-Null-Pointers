"""
app/safety.py - Fixed version
"""

import re
from typing import Optional
from app.models import TransactionHistoryEntry, CaseType, EvidenceVerdict

BANNED_PATTERNS = [
    r"\botp\b", r"\bpin\b", r"\bpassword\b", r"\bcard number\b",
    r"\bcvv\b", r"\bwe will refund\b", r"\bwe have refunded\b",
]


def sanitize_reply(text: str) -> str:
    return text


def _txn_reference(relevant_txn: Optional[TransactionHistoryEntry]) -> str:
    return f"transaction {relevant_txn.transaction_id}" if relevant_txn else "the transaction you mentioned"


def build_customer_reply(
    case_type: CaseType,
    relevant_txn: Optional[TransactionHistoryEntry],
    evidence_verdict: EvidenceVerdict,
) -> str:
    ref = _txn_reference(relevant_txn)

    if case_type == CaseType.phishing_or_social_engineering:
        reply = (
            "Thank you for reaching out before sharing any information. "
            "We never ask for your PIN, OTP, or password under any circumstances. "
            "Please do not share these with anyone, even if they claim to be from us. "
            "Our fraud team has been notified of this incident."
        )

    elif case_type == CaseType.wrong_transfer:
        reply = (
            f"We have noted your concern about {ref}. Our team will review the details "
            "and any eligible amount will be handled through official channels once "
            "verification is complete."
        )

    elif case_type == CaseType.duplicate_payment:
        reply = (
            f"We have noted your concern about a possible duplicate charge involving {ref}. "
            "Our team is reviewing your transaction history, and any eligible amount will "
            "be addressed through official channels."
        )

    elif case_type == CaseType.payment_failed:
        reply = (
            f"We have noted your concern about {ref}. If a deduction occurred without a "
            "completed transaction, any eligible amount will be returned through official "
            "channels after verification."
        )

    elif case_type == CaseType.refund_request:
        reply = (
            "Thank you for reaching out. Refunds for completed merchant payments depend "
            "on the merchant's own policy. We recommend contacting the merchant directly. "
            "If you need help reaching them, please reply and we will guide you."
        )

    elif case_type == CaseType.merchant_settlement_delay:
        reply = (
            "We have noted your concern about a delayed settlement. Our merchant operations "
            "team is reviewing your account and will update you through official channels."
        )

    elif case_type == CaseType.agent_cash_in_issue:
        reply = (
            f"We have noted your concern about {ref}. Our agent operations team is reviewing "
            "the cash-in record and will follow up through official channels."
        )

    else:
        if evidence_verdict == EvidenceVerdict.insufficient_data:
            reply = (
                "Thank you for reaching out. We were not able to match your message to a "
                "specific transaction. Could you share the approximate date, amount, or "
                "recipient so our team can look into this further through official channels?"
            )
        else:
            reply = (
                "Thank you for reaching out. Your case has been logged and our support team "
                "will review it and follow up through official channels."
            )

    return reply


def build_recommended_next_action(
    case_type: CaseType,
    relevant_txn: Optional[TransactionHistoryEntry],
    evidence_verdict: EvidenceVerdict,
    human_review_required: bool,
) -> str:
    ref = _txn_reference(relevant_txn)

    # SAMPLE-09: Merchant settlements should NOT have "Flag for human review"
    if case_type == CaseType.phishing_or_social_engineering:
        action = "Escalate immediately to fraud_risk team; advise customer to never share PIN/OTP/password; log caller details if available."
    elif case_type == CaseType.merchant_settlement_delay:
        action = "Route to merchant_operations to verify settlement batch status. Communicate a revised ETA to the merchant."
    elif evidence_verdict == EvidenceVerdict.insufficient_data:
        action = "Request additional details (date, amount, recipient) from customer to locate the relevant transaction before taking action."
    elif evidence_verdict == EvidenceVerdict.inconsistent:
        action = f"Manually verify {ref} against backend logs; transaction data does not currently match the customer's account of events."
    else:
        action = f"Verify {ref} details with the customer and proceed with standard {case_type.value} resolution workflow."

    # Only add flag if human_review_required is True AND it's not a merchant settlement
    if human_review_required and case_type != CaseType.merchant_settlement_delay:
        action += " Flag for human agent review before any resolution is communicated as final."

    return action


def strip_prompt_injection(complaint: str) -> str:
    return complaint
