# app/runner_setup.py
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.adk.memory import InMemoryMemoryService
from google.adk.models.google_llm import Gemini
from app.agents import build_dealmaker_agent
from google.genai import types

# Retry config like course notebooks
retry_config = types.HttpRetryOptions(attempts=3, initial_delay=1, exp_base=2)

# Model instance
model = Gemini(model="gemini-2.5-flash-lite", retry_options=retry_config)

# Build agent
dealmaker_agent = build_dealmaker_agent(model, retry_config)

# Session + Memory services
session_service = InMemorySessionService()
memory_service = InMemoryMemoryService()

# Create Runner with both services (enables memory tools)
runner = Runner(
    agent=dealmaker_agent,
    app_name="DealmakerApp",
    session_service=session_service,
    memory_service=memory_service,
)
