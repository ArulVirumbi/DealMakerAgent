# app/tools/comms_tool.py
from google.adk.tools import FunctionTool
from app.observability import log_event

def send_email_fn(to: str, subject:str, body:str, session_id: str=None):
    # demo stub; replace with SMTP/Twilio call
    msg = {"to":to,"subject":subject,"body":body}
    log_event(session_id=session_id, actor="CommsTool", action="send_email", payload=msg)
    return {"status":"sent","message_id":"demo-msg-1"}

def send_whatsapp_fn(number: str, text: str, session_id: str=None):
    msg = {"to":number,"text":text}
    log_event(session_id=session_id, actor="CommsTool", action="send_whatsapp", payload=msg)
    return {"status":"sent","message_id":"demo-wa-1"}

email_tool = FunctionTool(name="send_email", fn=send_email_fn, description="Send email")
whatsapp_tool = FunctionTool(name="send_whatsapp", fn=send_whatsapp_fn, description="Send WhatsApp message")
