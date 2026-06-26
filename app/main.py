"""
app/main.py

FastAPI app exposing GET /health and POST /analyze-ticket. Wires
together evidence.py, classifier.py, and safety.py. Never returns
stack traces or secrets.
"""

import logging
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from pydantic import ValidationError

from app.models import AnalyzeTicketRequest, AnalyzeTicketResponse
from app.evidence import investigate
from app.classifier import classify_case
from app.safety import build_customer_reply, build_recommended_next_action, strip_prompt_injection

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("ticket-triage")

app = FastAPI(title="Ticket Triage Copilot")


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/analyze-ticket")
async def analyze_ticket(request: Request):
    try:
        raw_body = await request.json()
    except Exception:
        return JSONResponse(status_code=400, content={"error": "Malformed JSON body."})

    try:
        ticket = AnalyzeTicketRequest(**raw_body)
    except ValidationError as e:
        return JSONResponse(status_code=400, content={"error": f"Missing or invalid required fields: {str(e)}"})

    if not ticket.complaint or not ticket.complaint.strip():
        return JSONResponse(status_code=422, content={"error": "complaint must not be empty."})

    try:
        safe_complaint = strip_prompt_injection(ticket.complaint)

        relevant_txn, evidence_verdict = investigate(safe_complaint, ticket.transaction_history or [])

        case_type, severity, department, human_review_required, confidence, reason_codes = classify_case(
            complaint=safe_complaint,
            user_type=ticket.user_type.value if ticket.user_type else None,
            relevant_txn=relevant_txn,
            evidence_verdict=evidence_verdict,
        )

        customer_reply = build_customer_reply(case_type, relevant_txn, evidence_verdict)
        recommended_next_action = build_recommended_next_action(
            case_type, relevant_txn, evidence_verdict, human_review_required
        )

        agent_summary = (
            f"{ticket.user_type.value.capitalize() if ticket.user_type else 'Customer'} "
            f"reported a {case_type.value.replace('_', ' ')} case"
            f"{f' involving {relevant_txn.transaction_id}' if relevant_txn else ' with no matching transaction found'}."
        )

        response = AnalyzeTicketResponse(
            ticket_id=ticket.ticket_id,
            relevant_transaction_id=relevant_txn.transaction_id if relevant_txn else None,
            evidence_verdict=evidence_verdict,
            case_type=case_type,
            severity=severity,
            department=department,
            agent_summary=agent_summary,
            recommended_next_action=recommended_next_action,
            customer_reply=customer_reply,
            human_review_required=human_review_required,
            confidence=confidence,
            reason_codes=reason_codes,
        )

        return JSONResponse(status_code=200, content=response.model_dump())

    except Exception as e:
        logger.exception("Unhandled error while analyzing ticket %s", ticket.ticket_id)
        return JSONResponse(status_code=500, content={"error": "Internal error while processing ticket."})
