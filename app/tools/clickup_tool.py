# app/tools/clickup_tool.py
from google.adk.tools import FunctionTool, ToolContext
from app.observability import log_event

# Creates an approval task (returns an approval token/invocation_id for resuming)
def request_approval_fn(session_id: str, summary: str, tool_context: ToolContext = None):
    # Use tool_context.request_confirmation in ADK tools that support it (we simulate)
    # For demo, return a 'pending' object with an approval_id.
    approval_id = f"approval-{session_id}-{int(tool_context.invocation_id or 0)}" if tool_context else f"approval-{session_id}"
    payload = {"approval_id": approval_id, "status":"PENDING", "summary": summary}
    log_event(session_id=session_id, actor="ClickUpTool", action="create_approval", payload=payload)
    # ADK real pattern: tool_context.request_confirmation(...) - here we return pending
    return {"status":"PENDING", "approval_id": approval_id}

clickup_approval_tool = FunctionTool(
    name="request_approval",
    fn=request_approval_fn,
    description="Create a human approval task and pause execution until resolved"
)
