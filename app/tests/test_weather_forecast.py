"""Unit tests for weather_forecast tool

Note: These tests require the full environment with dependencies installed.
Run after: pip install -r requirements.txt
"""

import sys
import os
import asyncio

# Add parent directory to path to import tools
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))


async def test_mock_weather_data():
    """Test mock weather data generation"""
    from tools.weather_forecast import _get_mock_weather_data
    
    result = _get_mock_weather_data("Berlin", "Germany")
    assert result is not None
    assert "location" in result
    assert "Berlin" in result["location"]
    assert "temperature_c" in result
    assert "conditions" in result
    print("✓ test_mock_weather_data passed")


async def test_date_validation():
    """Test date validation logic"""
    from tools.weather_forecast import validate_date
    from datetime import datetime, timedelta
    
    # Valid date (tomorrow)
    tomorrow = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")
    assert validate_date(tomorrow) == True
    
    # Invalid date (too far in future)
    far_future = (datetime.now() + timedelta(days=10)).strftime("%Y-%m-%d")
    assert validate_date(far_future) == False
    
    # Invalid format
    assert validate_date("invalid-date") == False
    
    print("✓ test_date_validation passed")


async def test_weather_response_formatting():
    """Test weather response formatting"""
    from tools.weather_forecast import format_weather_response
    
    mock_data = {
        "location": "Berlin, Germany",
        "date": "2024-01-20",
        "temperature_c": 5,
        "temperature_f": 41,
        "conditions": "partly cloudy",
        "precipitation_prob": 20,
        "wind_speed": 15,
        "humidity": 65
    }
    
    result = format_weather_response(mock_data, "TechVentures GmbH")
    assert "Berlin" in result
    assert "TechVentures GmbH" in result
    assert "5°C" in result or "5" in result
    assert "partly cloudy" in result
    
    print("✓ test_weather_response_formatting passed")


async def test_weather_tool_invalid_location():
    """Test weather tool with invalid location format"""
    from tools.weather_forecast import weather_forecast
    
    result = await weather_forecast.ainvoke({"location": "InvalidFormat"})
    assert "Invalid location format" in result
    
    print("✓ test_weather_tool_invalid_location passed")


async def test_weather_tool_valid_location():
    """Test weather tool with valid location (using mock data)"""
    from tools.weather_forecast import weather_forecast
    
    # This will use mock data since no API key is set
    result = await weather_forecast.ainvoke({"location": "Berlin, Germany"})
    assert "Berlin" in result
    assert "°C" in result or "°F" in result
    
    print("✓ test_weather_tool_valid_location passed")


if __name__ == "__main__":
    print("Running weather_forecast tests...")
    print("Note: Tests use mock data (no API key required)\n")
    
    try:
        asyncio.run(test_mock_weather_data())
        asyncio.run(test_date_validation())
        asyncio.run(test_weather_response_formatting())
        asyncio.run(test_weather_tool_invalid_location())
        asyncio.run(test_weather_tool_valid_location())
        
        print("\nAll weather_forecast tests passed! ✓")
    except Exception as e:
        print(f"\n✗ Test failed: {e}")
        import traceback
        traceback.print_exc()
