# app/observability.py
import logging
import json
from opentelemetry import trace

# Basic structured logger
logger = logging.getLogger("dealmaker")
logger.setLevel(logging.DEBUG)
handler = logging.StreamHandler()
formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)

tracer = trace.get_tracer(__name__)

def log_event(session_id, actor, action, payload):
    logger.info(json.dumps({
        "session_id": session_id,
        "actor": actor,
        "action": action,
        "payload": payload
    }))
