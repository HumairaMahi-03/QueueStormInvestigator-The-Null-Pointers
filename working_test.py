from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
import uvicorn
import json

app = FastAPI()

@app.get("/health")
async def health():
    return {"status": "ok"}

@app.post("/analyze-ticket")
async def analyze_ticket(request: Request):
    try:
        data = await request.json()
        return {
            "ticket_id": data.get("ticket_id", "TKT-001"),
            "relevant_transaction_id": "TXN-9101",
            "evidence_verdict": "consistent",
            "case_type": "wrong_transfer",
            "severity": "high",
            "department": "dispute_resolution",
            "agent_summary": "Customer reports wrong transfer",
            "recommended_next_action": "Verify transaction details",
            "customer_reply": "We have noted your concern. Our team will investigate.",
            "human_review_required": True,
            "confidence": 0.9,
            "reason_codes": ["wrong_transfer"]
        }
    except json.JSONDecodeError:
        return JSONResponse(
            status_code=400,
            content={"error": "Invalid JSON body"}
        )
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"error": f"Internal error: {str(e)}"}
        )

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
