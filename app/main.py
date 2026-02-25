# CRITICAL: Initialize telemetry BEFORE importing AI frameworks (LangChain, LiteLLM, etc.)
from application_foundation.aicore import set_aicore_config
from application_foundation.common.telemetry import auto_instrument

set_aicore_config()
auto_instrument()  # Must be called before importing LangChain/LiteLLM

# Now safe to import AI frameworks and other dependencies
import logging
import os

import click
import uvicorn
from a2a.server.apps import A2AStarletteApplication
from a2a.server.request_handlers import DefaultRequestHandler
from a2a.server.tasks import InMemoryTaskStore
from a2a.types import AgentCapabilities, AgentCard, AgentSkill

from agent_executor import AgentExecutor

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

HOST = os.environ.get("HOST", "0.0.0.0")
PORT = int(os.environ.get("PORT", "5000"))


@click.command()
@click.option("--host", default=HOST)
@click.option("--port", default=PORT)
def main(host: str, port: int):
    """
    Start the Weather Agent A2A server.
    
    The agent helps users plan business trips by combining business partner
    information with weather forecasts.
    """
    skill = AgentSkill(
        id="weather-agent",
        name="Weather Agent",
        description="AI agent that combines business partner data with weather forecasts for intelligent trip planning.",
        tags=["weather", "business-partner", "trip-planning", "langgraph"],
        examples=[
            "What's the weather for my visit to Acme Corp next week?",
            "Where is TechVentures GmbH located?",
            "What's the weather in Berlin on March 15?",
            "Show me the weather at Acme Corp today"
        ],
    )
    
    agent_card = AgentCard(
        name="Weather Agent for SAP Concur",
        description=(
            "An AI-powered conversational agent that integrates SAP S/4HANA business partner data "
            "with weather forecasts to help users plan business trips intelligently. "
            "Ask questions like 'What's the weather for my visit to Acme Corp next week?' "
            "to get integrated trip planning insights."
        ),
        url=os.environ.get("AGENT_PUBLIC_URL", f"http://{host}:{port}/"),
        version="1.0.0",
        defaultInputModes=["text", "text/plain"],
        defaultOutputModes=["text", "text/plain"],
        capabilities=AgentCapabilities(streaming=True, pushNotifications=False),
        skills=[skill],
    )
    
    server = A2AStarletteApplication(
        agent_card=agent_card,
        http_handler=DefaultRequestHandler(
            agent_executor=AgentExecutor(),
            task_store=InMemoryTaskStore(),
        ),
    )
    
    logger.info(f"Starting Weather Agent A2A server at http://{host}:{port}")
    logger.info("Agent capabilities:")
    logger.info("  - Business partner lookup (fuzzy matching)")
    logger.info("  - Weather forecasts (7-day)")
    logger.info("  - Integrated trip planning")
    logger.info("  - Streaming responses")
    
    uvicorn.run(server.build(), host=host, port=port)


if __name__ == "__main__":
    main()
