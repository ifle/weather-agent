# Manual Testing Guide for Weather Agent

This guide provides sample queries to manually test the Weather Agent functionality.

## Prerequisites

The agent requires a full environment with dependencies installed:
```bash
pip install -r requirements.txt
```

For local testing, you'll need:
- SAP Artifactory credentials
- SAP AI Core configuration
- (Optional) OpenWeatherMap API key

See `app/.env.example` for required environment variables.

## Sample Test Queries

### 1. Integrated Trip Planning (Primary Use Case)
```
Query: "What's the weather for my visit to Acme Corp next week?"

Expected behavior:
- Agent looks up Acme Corp (finds: New York, USA)
- Agent retrieves weather forecast for New York
- Response includes partner name, location, and weather details
```

### 2. Business Partner Lookup
```
Query: "Where is TechVentures GmbH located?"

Expected behavior:
- Agent searches for TechVentures GmbH
- Response: Berlin, Germany
```

### 3. Simple Weather Query
```
Query: "What's the weather in Berlin today?"

Expected behavior:
- Agent retrieves current weather for Berlin
- Response includes temperature, conditions, precipitation
```

### 4. Date-Specific Weather
```
Query: "What's the weather at Acme Corp on March 15?"

Expected behavior:
- Agent looks up Acme Corp location
- Agent retrieves weather for March 15
- Response includes date-specific forecast
```

### 5. Partial Partner Name
```
Query: "What's the weather at Tech?"

Expected behavior:
- Agent finds TechVentures GmbH (partial match)
- Agent retrieves weather for Berlin
```

### 6. Case-Insensitive Search
```
Query: "weather at ACME CORP?"

Expected behavior:
- Agent finds Acme Corp (case-insensitive)
- Agent retrieves weather for New York
```

### 7. Follow-up Question (Context Management)
```
First query: "What's the weather for my visit to Acme Corp?"
Follow-up: "What about Friday?"

Expected behavior:
- Agent remembers Acme Corp from previous query
- Agent retrieves weather for Friday in New York
```

### 8. Partner Not Found
```
Query: "What's the weather at NonExistent Company?"

Expected behavior:
- Agent reports partner not found
- Agent suggests checking spelling or provides alternatives
```

### 9. Multiple Partners (Test Diversity)
```
Queries to test different locations:
- "Weather at Pacific Solutions?" (Tokyo, Japan)
- "Where is Nordic Systems AB?" (Stockholm, Sweden)
- "Weather at Alpine Technologies?" (Zurich, Switzerland)
- "Where is Southern Cross Enterprises?" (Sydney, Australia)
```

### 10. Actionable Insights
```
Query: "What's the weather for my visit to TechVentures GmbH tomorrow?"

Expected behavior:
- If high precipitation: "Pack an umbrella"
- If cold: "Dress warmly"
- If hot: "Stay hydrated"
```

## Expected Response Format

All responses should be:
- ✅ Conversational and natural
- ✅ Include partner name (if applicable)
- ✅ Include location (city, country)
- ✅ Include temperature in both C and F
- ✅ Include weather conditions
- ✅ Include actionable advice when relevant
- ✅ Handle errors gracefully

## Mock Data Reference

The agent uses 10 mock business partners:

| ID | Name | City | Country |
|----|------|------|---------|
| BP001 | Acme Corp | New York | USA |
| BP002 | TechVentures GmbH | Berlin | Germany |
| BP003 | Global Innovations Ltd | London | UK |
| BP004 | Pacific Solutions | Tokyo | Japan |
| BP005 | Nordic Systems AB | Stockholm | Sweden |
| BP006 | Alpine Technologies SA | Zurich | Switzerland |
| BP007 | Southern Cross Enterprises | Sydney | Australia |
| BP008 | Maple Leaf Industries | Toronto | Canada |
| BP009 | Dragon Tech Co | Shanghai | China |
| BP010 | Sunset Digital | San Francisco | USA |

## Running the Agent Locally

For detailed instructions on running the agent locally, use the `appfnd-agent-run-local` skill.

Quick start (requires environment setup):
```bash
python app/main.py --host 0.0.0.0 --port 5000
```

## Notes

- **Mock Data**: Uses hardcoded partners and mock weather data (no real API calls during development)
- **Context**: Agent maintains last 5 messages for follow-up questions
- **Streaming**: All responses are streamed via A2A protocol
- **Error Handling**: Graceful degradation if weather API fails
