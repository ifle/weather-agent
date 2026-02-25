# Weather Agent for SAP Concur

An AI-powered conversational agent that integrates Ariba business partner data (via MCP server) with weather forecasts to help users plan business trips intelligently.

## Overview

The Weather Agent provides:
- **Integrated Trip Planning**: Combines business partner locations with weather forecasts
- **Natural Language Interface**: Ask questions like "What's the weather for my visit to Acme Corp next week?"
- **Ariba MCP Integration**: Real-time business partner lookup from Ariba system
- **Weather Forecasts**: 7-day forecasts with actionable travel insights

Built with:
- **A2A Protocol**: For agent-to-agent communication
- **LangGraph**: For agent orchestration with tool-based architecture
- **LiteLLM**: For model abstraction (Claude 3.5 Sonnet via SAP AI Core)
- **Application Foundation SDK**: For SAP AI Core integration and observability
- **Ariba MCP Server**: For real-time business partner data

## Project Structure

- `app.yaml` - App Foundation workload configuration
- `Dockerfile` - Container build configuration
- `app/main.py` - A2A server entry point
- `app/agent_executor.py` - Request handling and task management
- `app/agent.py` - Core agent logic with LangGraph
- `app/tools/business_partner_lookup.py` - Ariba MCP integration
- `app/tools/weather_forecast.py` - Weather forecast retrieval tool

## Features

### Must-Have (MVP)
✅ Natural language query understanding  
✅ Business partner lookup via Ariba MCP server  
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

The agent connects to the Ariba MCP server to retrieve business partner data:

**Default URL**: `https://mcp-server-demo-igor-dev.c-127c9ef.stage.kyma.ondemand.com/mcp/ariba`

To use a different MCP server, set the environment variable:
```bash
ARIBA_MCP_SERVER_URL=https://your-mcp-server-url/mcp/ariba
```

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
- **Business Partner Data**: Real-time via Ariba MCP server
- **Resources**: 256Mi-512Mi memory, 50m-200m CPU
- **Observability**: OpenTelemetry auto-instrumentation with App Foundation SDK

## Architecture

```
User Query
    ↓
WeatherAgent (LangGraph)
    ↓
    ├─→ Business Partner Lookup Tool → Ariba MCP Server
    │                                      ↓
    │                                   Partner Data
    │                                      ↓
    └─→ Weather Forecast Tool ──────→ OpenWeatherMap API
                                           ↓
                                      Weather Data
                                           ↓
                                    Combined Response
```
