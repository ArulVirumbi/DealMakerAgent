# app/agents.py
from google.adk.agents import LlmAgent
from google.adk.models.google_llm import Gemini
from google.adk.tools import AgentTool, load_memory, preload_memory, FunctionTool
from app.observability import log_event
from google.genai import types
from app.tools import calendar_tool, comms_tool, clickup_tool
from google.adk.agents import Agent

# create subagents as small LlmAgent instances with clear instructions.
def make_intake_agent(model, retry_config):
    return LlmAgent(
        name="IntakeAgent",
        model=model,
        instruction="Parse an incoming lead_text into structured fields: client, event_type, requested_slots, budget, services, location, contact.",
    )

def make_availability_agent(model, retry_config):
    # This agent will call calendar_freebusy and calendar_create_tentative tools
    return LlmAgent(
        name="AvailabilityAgent",
        model=model,
        instruction="Given requested_slots, check calendar_freebusy, propose alternatives, and (if allowed) create a tentative hold using calendar_create_tentative.",
        tools=[calendar_tool.calendar_freebusy_tool, calendar_tool.calendar_tentative_tool],
        output_key="availability"
    )

def make_value_agent(model, retry_config):
    # uses memory retrieval tools
    return LlmAgent(
        name="ValueAgent",
        model=model,
        instruction="Use load_memory to fetch past deal summaries for similar events. Based on that and rules, propose min_price, target_price, red_line.",
        tools=[load_memory],
        output_key="valuation"
    )

def make_negotiation_agent(model, retry_config):
    return LlmAgent(
        name="NegotiationAgent",
        model=model,
        instruction="Draft negotiation messages, parse replies, and propose counteroffers. Use send_email/send_whatsapp tool for sending messages.",
        tools=[comms_tool.email_tool, comms_tool.whatsapp_tool],
        output_key="negotiation_step"
    )

def make_critic_agent(model, retry_config):
    return LlmAgent(
        name="SimulationCriticAgent",
        model=model,
        instruction="Simulate negotiation trajectories and score them with short risk/reward analysis.",
        output_key="simulation"
    )

def make_policy_agent(model, retry_config):
    return LlmAgent(
        name="PolicyAgent",
        model=model,
        instruction="Given an action and valuation, decide if human approval is required and if so, call request_approval.",
        tools=[clickup_tool.clickup_approval_tool]
    )

def make_contract_agent(model, retry_config):
    return LlmAgent(
        name="ContractAgent",
        model=model,
        instruction="Generate contract text/summary, confirm calendar via calendar_confirm_event tool, and return contract reference.",
        tools=[calendar_tool.calendar_confirm_tool]
    )

# Root Dealmaker: orchestrator that will call subagents as AgentTool
def build_dealmaker_agent(model, retry_config):
    Intake = make_intake_agent(model, retry_config)
    Availability = make_availability_agent(model, retry_config)
    Value = make_value_agent(model, retry_config)
    Negotiation = make_negotiation_agent(model, retry_config)
    Critic = make_critic_agent(model, retry_config)
    Policy = make_policy_agent(model, retry_config)
    Contract = make_contract_agent(model, retry_config)

    # Wrap subagents as tools the root can call:
    agent_tools = [
        AgentTool(Intake, name="IntakeAgentTool"),
        AgentTool(Availability, name="AvailabilityAgentTool"),
        AgentTool(Value, name="ValueAgentTool"),
        AgentTool(Negotiation, name="NegotiationAgentTool"),
        AgentTool(Critic, name="CriticAgentTool"),
        AgentTool(Policy, name="PolicyAgentTool"),
        AgentTool(Contract, name="ContractAgentTool"),
        load_memory
    ]

    root_instruction = """
You are Dealmaker: orchestrate the negotiation lifecycle.
1) Call IntakeAgentTool to parse lead_text.
2) Call AvailabilityAgentTool to check calendar and create tentative hold if free.
3) Call ValueAgentTool to compute pricing using memory.
4) Enter negotiation loop by calling NegotiationAgentTool; after each candidate reply use CriticAgentTool to simulate.
5) If PolicyAgentTool indicates approval needed, pause/resume via request_approval tool.
6) On acceptance, call ContractAgentTool to finalize.
Return a concise JSON outcome.
"""
    root = LlmAgent(
        name="Dealmaker",
        model=model,
        instruction=root_instruction,
        tools=agent_tools,
    )
    return root
