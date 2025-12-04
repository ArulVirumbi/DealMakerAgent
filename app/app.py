# app/app.py
import uvicorn
from fastapi import FastAPI, BackgroundTasks
from pydantic import BaseModel
from app.runner_setup import runner, session_service
from app.observability import log_event
from google.genai import types
import asyncio

app = FastAPI(title="Dealmaker ADK Demo")

class LeadIn(BaseModel):
    lead_text: str

@app.post("/lead")
async def submit_lead(payload: LeadIn):
    # Create a session via ADK session_service
    session = await session_service.create_session(app_name="DealmakerApp", user_id="owner", session_id=None)
    sid = session.id
    log_event(sid, "API", "receive_lead", {"text": payload.lead_text})

    # Construct user message content for runner and run a single turn
    content = types.Content(role="user", parts=[types.Part(text=payload.lead_text)])
    # Kick off runner run_async — but for demo we'll run synchronously using run_async and collect final response
    async for event in runner.run_async(user_id="owner", session_id=sid, new_message=content):
        # When final response, return the text and session_id
        if event.is_final_response():
            text = event.content.parts[0].text if event.content and event.content.parts else ""
            log_event(sid, "Runner", "final_response", {"text": text})
            return {"session_id": sid, "final_text": text}
    return {"session_id": sid, "status":"started"}

class ReplyIn(BaseModel):
    session_id: str
    reply_text: str

@app.post("/webhook/reply")
async def reply(payload: ReplyIn):
    # Append client reply and feed to runner (simulate webhook)
    content = types.Content(role="user", parts=[types.Part(text=payload.reply_text)])
    async for event in runner.run_async(user_id="owner", session_id=payload.session_id, new_message=content):
        if event.is_final_response():
            text = event.content.parts[0].text if event.content and event.content.parts else ""
            log_event(payload.session_id, "Runner", "final_response_reply", {"text": text})
            return {"status":"ok","text":text}
    return {"status":"ok","msg":"processing"}

# ClickUp-like webhook to approve by external actor
class ApprovalIn(BaseModel):
    approval_id: str
    decision: str  # APPROVED / DECLINED

@app.post("/clickup/webhook")
async def clickup_webhook(payload: ApprovalIn):
    # In a real flow, map approval_id->invocation_id and resume runner.run_async with a FunctionResponse
    # For demo, just log and mark session
    # You can wire ADK's request_confirmation resume pattern per the MCP notebooks.
    log_event(None, "ClickUpWebhook", "approval", {"approval_id": payload.approval_id, "decision": payload.decision})
    return {"status":"ack"}
