# Weather Agent for SAP Concur

An AI-powered conversational agent that integrates Ariba business partner data (via MCP server) with weather forecasts to help users plan business trips intelligently.

## Overview

The Weather Agent provides:
- **Integrated Trip Planning**: Combines business partner locations with weather forecasts
- **Natural Language Interface**: Ask questions like "What's the weather for my visit to Acme Corp next week?"
- **Ariba MCP Integration**: Real-time business partner lookup using Model Context Protocol (MCP)
- **Weather Forecasts**: 7-day forecasts with actionable travel insights

Built with:
- **A2A Protocol**: For agent-to-agent communication
- **LangGraph**: For agent orchestration with tool-based architecture
- **LiteLLM**: For model abstraction (Claude 3.5 Sonnet via SAP AI Core)
- **Application Foundation SDK**: For SAP AI Core integration and observability
- **MCP (Model Context Protocol)**: For direct LLM access to Ariba business partner tools

## Project Structure

- `app.yaml` - App Foundation workload configuration with MCP server integration
- `Dockerfile` - Container build configuration
- `app/main.py` - A2A server entry point
- `app/agent_executor.py` - Request handling and task management
- `app/agent.py` - Core agent logic with LangGraph and MCP integration
- `app/tools/business_partner_lookup.py` - MCP tool reference
- `app/tools/weather_forecast.py` - Weather forecast retrieval tool

## Features

### Must-Have (MVP)
✅ Natural language query understanding  
✅ Business partner lookup via Ariba MCP server (direct LLM tool calling)  
✅ Weather forecast integration (7-day)  
✅ Integrated trip planning (partner + weather + date)  
✅ Streaming responses via A2A protocol  
✅ Conversation context management  

### High-Want (Phase 2)
🔲 Multi-location trip support  
🔲 Proactive weather notifications  

### Nice-to-Have (Phase 3)
🔲 Historical weather data  
🔲 Travel recommendations  

## Configuration

### Ariba MCP Server

The agent uses Model Context Protocol (MCP) to give the LLM direct access to Ariba business partner tools.

**MCP Server URL**: `https://mcp-server-demo-igor-dev.c-127c9ef.stage.kyma.ondemand.com/mcp/ariba`

The MCP server is configured in `app.yaml`:
```yaml
mcpServers:
- name: ariba
  url: https://mcp-server-demo-igor-dev.c-127c9ef.stage.kyma.ondemand.com/mcp/ariba
```

The LLM can directly call tools provided by the MCP server, including:
- Business partner search
- Business partner details retrieval
- Location information extraction

## Local Development

Running locally requires SAP Artifactory credentials and AI Core configuration due to internal SDK dependencies.

**For detailed local development instructions, use the `appfnd-agent-run-local` skill.**

## Sample Queries

- "What's the weather for my visit to Acme Corp next week?"
- "Where is TechVentures GmbH located?"
- "What's the weather in Berlin on March 15?"
- "Show me the weather at Acme Corp today"
- "What about Friday?" (follow-up question)

## Technical Details

- **Model**: Claude 3.5 Sonnet (anthropic--claude-4.5-sonnet)
- **Weather API**: OpenWeatherMap (7-day forecasts)
- **Business Partner Data**: Real-time via Ariba MCP server (MCP protocol)
- **Resources**: 256Mi-512Mi memory, 50m-200m CPU
- **Observability**: OpenTelemetry auto-instrumentation with App Foundation SDK

## Architecture

```
User Query
    ↓
WeatherAgent (LangGraph)
    ↓
LLM (Claude 3.5 Sonnet)
    ↓
    ├─→ MCP Tools (Ariba) ──→ Business Partner Data
    │                             ↓
    └─→ Weather Forecast Tool → OpenWeatherMap API
                                     ↓
                                Weather Data
                                     ↓
                              Combined Response
```

### MCP Integration

The agent uses the Model Context Protocol (MCP) to provide the LLM with direct access to Ariba business partner tools. This allows the LLM to:
1. Discover available tools from the MCP server
2. Call tools directly with natural language understanding
3. Process tool responses and combine them with other data sources

The MCP server exposes business partner search and retrieval tools that the LLM can invoke as needed.
