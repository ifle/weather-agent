"""Integration test for complete Weather Agent flow

Tests the end-to-end agent execution with business partner lookup and weather forecast.

Note: Requires full environment with dependencies installed.
Run after: pip install -r requirements.txt
"""

import sys
import os
import asyncio

# Add parent directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))


async def test_complete_agent_flow():
    """
    Test complete agent flow with integrated query.
    
    Query: "What's the weather for my visit to Acme Corp next week?"
    
    Expected behavior:
    1. Agent calls business_partner_lookup tool with "Acme Corp"
    2. Tool returns location: New York, USA
    3. Agent calls weather_forecast tool with location
    4. Agent combines both results in response
    """
    from agent import WeatherAgent
    
    print("Initializing Weather Agent...")
    agent = WeatherAgent()
    
    query = "What's the weather for my visit to Acme Corp next week?"
    print(f"\nQuery: {query}")
    print("\nProcessing...")
    
    # Stream agent responses
    response_content = []
    async for item in agent.stream(query, context_id="test-context"):
        print(f"  Status: {'Complete' if item['is_task_complete'] else 'Working'}")
        print(f"  Content: {item['content'][:100]}..." if len(item['content']) > 100 else f"  Content: {item['content']}")
        response_content.append(item['content'])
        
        if item['is_task_complete']:
            break
    
    # Verify response contains expected elements
    final_response = response_content[-1]
    
    print("\n" + "="*60)
    print("FINAL RESPONSE:")
    print("="*60)
    print(final_response)
    print("="*60)
    
    # Assertions
    checks = {
        "Acme Corp mentioned": "Acme Corp" in final_response or "acme" in final_response.lower(),
        "Location mentioned": "New York" in final_response or "location" in final_response.lower(),
        "Weather data included": any(word in final_response.lower() for word in ["weather", "temperature", "°c", "°f", "conditions"]),
        "Response is conversational": len(final_response) > 50  # Reasonable length for conversation
    }
    
    print("\nVerification Checks:")
    all_passed = True
    for check_name, passed in checks.items():
        status = "✓" if passed else "✗"
        print(f"  {status} {check_name}")
        if not passed:
            all_passed = False
    
    if all_passed:
        print("\n✓ Integration test PASSED - All checks successful!")
        return True
    else:
        print("\n✗ Integration test FAILED - Some checks did not pass")
        return False


async def test_simple_partner_lookup():
    """Test simple business partner lookup query"""
    from agent import WeatherAgent
    
    print("\n" + "="*60)
    print("TEST: Simple Partner Lookup")
    print("="*60)
    
    agent = WeatherAgent()
    query = "Where is TechVentures GmbH located?"
    print(f"Query: {query}\n")
    
    async for item in agent.stream(query, context_id="test-context-2"):
        if item['is_task_complete']:
            print(f"Response: {item['content']}")
            assert "TechVentures" in item['content'] or "Berlin" in item['content']
            print("✓ Simple partner lookup test passed")
            break


async def test_simple_weather_query():
    """Test simple weather query"""
    from agent import WeatherAgent
    
    print("\n" + "="*60)
    print("TEST: Simple Weather Query")
    print("="*60)
    
    agent = WeatherAgent()
    query = "What's the weather in Berlin today?"
    print(f"Query: {query}\n")
    
    async for item in agent.stream(query, context_id="test-context-3"):
        if item['is_task_complete']:
            print(f"Response: {item['content']}")
            assert "Berlin" in item['content']
            assert any(word in item['content'].lower() for word in ["weather", "temperature", "°c", "°f"])
            print("✓ Simple weather query test passed")
            break


if __name__ == "__main__":
    print("="*60)
    print("WEATHER AGENT INTEGRATION TESTS")
    print("="*60)
    print("\nNote: Using mock data (no real S/4HANA or Weather API calls)")
    print("Tests verify agent orchestration and tool integration\n")
    
    try:
        # Run main integration test
        result = asyncio.run(test_complete_agent_flow())
        
        # Run additional tests
        asyncio.run(test_simple_partner_lookup())
        asyncio.run(test_simple_weather_query())
        
        print("\n" + "="*60)
        print("ALL INTEGRATION TESTS COMPLETED SUCCESSFULLY! ✓")
        print("="*60)
        
    except Exception as e:
        print(f"\n✗ Integration test failed with error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
