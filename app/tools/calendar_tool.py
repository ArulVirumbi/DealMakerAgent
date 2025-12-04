# app/tools/calendar_tool.py
from google.adk.tools import FunctionTool
from datetime import datetime, timedelta
from app.observability import log_event

# Simple function tool contract for freebusy/create/confirm
def freebusy_fn(request_slots: list):
    """
    request_slots: [{start_iso, end_iso}]
    returns: {"busy": bool, "details": ...}
    """
    # DEMO: mock busy==False for all slots
    result = {"busy": False, "details": []}
    log_event(session_id=request_slots and request_slots[0].get("session_id"), actor="CalendarTool", action="freebusy", payload=result)
    return {"status":"success","data":result}

def create_tentative_fn(title: str, start_iso: str, end_iso: str, ttl_hours: int=48, session_id: str=None):
    # In production, call Google Calendar API and set event status=tentative/holder
    event = {"id": f"evt_{start_iso}_{session_id}", "title": title, "start": start_iso, "end": end_iso, "status":"tentative", "expires_at": ttl_hours}
    log_event(session_id=session_id, actor="CalendarTool", action="create_tentative", payload=event)
    return {"status":"success","data":event}

def confirm_event_fn(event_id: str, session_id: str=None):
    log_event(session_id=session_id, actor="CalendarTool", action="confirm_event", payload={"event_id":event_id})
    return {"status":"success","data":{"event_id":event_id,"status":"confirmed"}}

calendar_freebusy_tool = FunctionTool(
    name="calendar_freebusy",
    fn=freebusy_fn,
    description="Check free/busy for given slots"
)

calendar_tentative_tool = FunctionTool(
    name="calendar_create_tentative",
    fn=create_tentative_fn,
    description="Create a tentative calendar hold"
)

calendar_confirm_tool = FunctionTool(
    name="calendar_confirm_event",
    fn=confirm_event_fn,
    description="Confirm an existing tentative calendar event"
)
