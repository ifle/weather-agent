"""Weather Agent

Core agent logic using LangGraph for orchestration with tool-based architecture.
Combines business partner lookup and weather forecast tools to provide integrated
trip planning assistance.
"""

import logging
from typing import AsyncGenerator, Literal
from dataclasses import dataclass

from langchain_core.messages import HumanMessage, SystemMessage, AIMessage
from langchain_litellm import ChatLiteLLM
from langgraph.graph import START, END, MessagesState, StateGraph
from langgraph.prebuilt import ToolNode

from tools.business_partner_lookup import business_partner_lookup, search_business_partner
from tools.weather_forecast import weather_forecast

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

SYSTEM_PROMPT = """You are a helpful AI assistant that helps users plan business trips by combining business partner information with weather forecasts.

Your capabilities:
1. Look up business partners by name and find their locations
2. Retrieve weather forecasts for any location
3. Combine partner data with weather information to provide integrated trip planning insights

When a user asks about weather for a partner visit:
1. First look up the business partner to find their location
2. Then get the weather forecast for that location
3. Provide a comprehensive response that includes both partner and weather information

Be conversational, friendly, and provide actionable travel advice based on weather conditions.
For example, if there's high chance of rain, suggest packing an umbrella.

Remember: You have access to tools for business partner lookup and weather forecasts. Use them to provide accurate, helpful information."""


@dataclass
class AgentResponse:
    status: Literal["input_required", "completed", "error"]
    message: str


class WeatherAgent:
    """
    Weather Agent with LangGraph-based orchestration.
    
    Uses two tools:
    - business_partner_lookup: Search for business partners
    - weather_forecast: Get weather forecasts
    """
    
    SUPPORTED_CONTENT_TYPES = ["text", "text/plain"]
    MAX_CONTEXT_MESSAGES = 5  # Keep last 5 messages for context
    
    def __init__(self):
        self.llm = ChatLiteLLM(model="sap/anthropic--claude-4.5-sonnet")
        self.tools = [business_partner_lookup, weather_forecast]
        self.graph = self._build_graph()
        logger.info("WeatherAgent initialized with LangGraph")
    
    def _build_graph(self):
        """
        Build the LangGraph state graph with tool support.
        
        Graph flow:
        START -> model -> [tools if needed] -> model -> END
        """
        # Bind tools to the LLM
        llm_with_tools = self.llm.bind_tools(self.tools)
        
        def call_model(state: MessagesState):
            """Call the LLM with current messages"""
            response = llm_with_tools.invoke(state["messages"])
            return {"messages": [response]}
        
        def should_continue(state: MessagesState) -> Literal["tools", "end"]:
            """Determine if we should call tools or end"""
            last_message = state["messages"][-1]
            # If the LLM makes a tool call, route to tools node
            if hasattr(last_message, "tool_calls") and last_message.tool_calls:
                return "tools"
            # Otherwise, end
            return "end"
        
        # Build the graph
        builder = StateGraph(MessagesState)
        
        # Add nodes
        builder.add_node("model", call_model)
        builder.add_node("tools", ToolNode(self.tools))
        
        # Add edges
        builder.add_edge(START, "model")
        builder.add_conditional_edges(
            "model",
            should_continue,
            {
                "tools": "tools",
                "end": END
            }
        )
        builder.add_edge("tools", "model")
        
        return builder.compile()
    
    def _prepare_messages(self, query: str, context_messages: list = None):
        """
        Prepare message list with system prompt, context, and current query.
        
        Args:
            query: Current user query
            context_messages: Previous conversation messages (optional)
            
        Returns:
            List of messages for the LLM
        """
        messages = [SystemMessage(content=SYSTEM_PROMPT)]
        
        # Add context messages (keep last MAX_CONTEXT_MESSAGES)
        if context_messages:
            messages.extend(context_messages[-self.MAX_CONTEXT_MESSAGES:])
        
        # Add current query
        messages.append(HumanMessage(content=query))
        
        return messages
    
    async def stream(self, query: str, context_id: str, context_messages: list = None) -> AsyncGenerator[dict, None]:
        """
        Stream agent responses with tool execution.
        
        Args:
            query: User query
            context_id: Conversation context identifier
            context_messages: Previous conversation messages
            
        Yields:
            Dictionary with status and content
        """
        logger.info(f"Processing query: {query}")
        
        # Initial status
        yield {
            "is_task_complete": False,
            "require_user_input": False,
            "content": "Processing your request..."
        }
        
        try:
            messages = self._prepare_messages(query, context_messages)
            
            # Stream the graph execution
            final_response = None
            async for event in self.graph.astream({"messages": messages}):
                # Extract the last message from each event
                if "messages" in event:
                    last_msg = event["messages"][-1]
                    if isinstance(last_msg, AIMessage) and not hasattr(last_msg, "tool_calls"):
                        final_response = last_msg.content
            
            if final_response:
                yield {
                    "is_task_complete": True,
                    "require_user_input": False,
                    "content": final_response
                }
            else:
                yield {
                    "is_task_complete": True,
                    "require_user_input": False,
                    "content": "I processed your request but couldn't generate a response. Please try again."
                }
                
        except Exception as e:
            logger.exception("Error processing query")
            yield {
                "is_task_complete": True,
                "require_user_input": False,
                "content": f"I encountered an error: {str(e)}. Please try again."
            }
    
    def invoke(self, query: str, context_id: str, context_messages: list = None) -> AgentResponse:
        """
        Synchronous invocation of the agent.
        
        Args:
            query: User query
            context_id: Conversation context identifier
            context_messages: Previous conversation messages
            
        Returns:
            AgentResponse with status and message
        """
        import asyncio
        
        try:
            messages = self._prepare_messages(query, context_messages)
            result = asyncio.run(self.graph.ainvoke({"messages": messages}))
            
            # Extract final response
            last_message = result["messages"][-1]
            if isinstance(last_message, AIMessage):
                return AgentResponse(
                    status="completed",
                    message=last_message.content
                )
            else:
                return AgentResponse(
                    status="error",
                    message="Unexpected response format"
                )
                
        except Exception as e:
            logger.exception("Error in synchronous invocation")
            return AgentResponse(
                status="error",
                message=f"Error: {str(e)}"
            )
