"""Weather Forecast Tool

This tool fetches weather forecasts for specified locations using OpenWeatherMap API.
Provides 7-day forecasts with temperature, conditions, and precipitation data.
"""

import os
from datetime import datetime, timedelta
from typing import Optional
import httpx
from langchain_core.tools import tool


class WeatherAPIError(Exception):
    """Raised when weather API request fails"""
    pass


async def get_weather_forecast_data(city: str, country: str, date: Optional[str] = None) -> dict:
    """
    Fetch weather forecast data from OpenWeatherMap API.
    
    Args:
        city: City name
        country: Country name or code
        date: Optional ISO date string (YYYY-MM-DD) within next 7 days
        
    Returns:
        Dictionary with weather data
        
    Raises:
        WeatherAPIError: If API request fails
    """
    # For development: Use mock data if API key not available
    api_key = os.getenv("OPENWEATHERMAP_API_KEY", "")
    
    if not api_key:
        # Return mock weather data for development
        return _get_mock_weather_data(city, country, date)
    
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            # First, geocode the location
            geo_url = "http://api.openweathermap.org/geo/1.0/direct"
            geo_params = {
                "q": f"{city},{country}",
                "limit": 1,
                "appid": api_key
            }
            
            geo_response = await client.get(geo_url, params=geo_params)
            geo_response.raise_for_status()
            geo_data = geo_response.json()
            
            if not geo_data:
                raise WeatherAPIError(f"Location '{city}, {country}' not found")
            
            lat = geo_data[0]["lat"]
            lon = geo_data[0]["lon"]
            
            # Get weather forecast
            forecast_url = "http://api.openweathermap.org/data/2.5/forecast"
            forecast_params = {
                "lat": lat,
                "lon": lon,
                "appid": api_key,
                "units": "metric"  # Celsius
            }
            
            forecast_response = await client.get(forecast_url, params=forecast_params)
            forecast_response.raise_for_status()
            forecast_data = forecast_response.json()
            
            return _process_forecast_data(forecast_data, date)
            
    except httpx.TimeoutException:
        raise WeatherAPIError("Weather API request timed out")
    except httpx.HTTPStatusError as e:
        if e.response.status_code == 429:
            raise WeatherAPIError("Weather API rate limit exceeded")
        raise WeatherAPIError(f"Weather API error: {e.response.status_code}")
    except Exception as e:
        raise WeatherAPIError(f"Weather API error: {str(e)}")


def _get_mock_weather_data(city: str, country: str, date: Optional[str] = None) -> dict:
    """
    Generate mock weather data for development.
    """
    # Simple mock data based on city (deterministic for consistency)
    temp_base = hash(city) % 20 + 10  # 10-30°C range
    
    target_date = datetime.now()
    if date:
        try:
            target_date = datetime.fromisoformat(date)
        except ValueError:
            pass
    
    return {
        "location": f"{city}, {country}",
        "date": target_date.strftime("%Y-%m-%d"),
        "temperature_c": temp_base,
        "temperature_f": round(temp_base * 9/5 + 32),
        "conditions": "partly cloudy",
        "precipitation_prob": 20,
        "wind_speed": 15,
        "humidity": 65
    }


def _process_forecast_data(forecast_data: dict, target_date: Optional[str] = None) -> dict:
    """
    Process OpenWeatherMap forecast data and extract relevant information.
    """
    if not forecast_data.get("list"):
        raise WeatherAPIError("Invalid forecast data received")
    
    # Get the first forecast entry (closest to target date)
    forecast = forecast_data["list"][0]
    
    temp_c = forecast["main"]["temp"]
    temp_f = round(temp_c * 9/5 + 32)
    
    return {
        "location": forecast_data["city"]["name"],
        "date": datetime.fromtimestamp(forecast["dt"]).strftime("%Y-%m-%d"),
        "temperature_c": round(temp_c),
        "temperature_f": temp_f,
        "conditions": forecast["weather"][0]["description"],
        "precipitation_prob": forecast.get("pop", 0) * 100,  # Probability of precipitation
        "wind_speed": forecast["wind"]["speed"],
        "humidity": forecast["main"]["humidity"]
    }


def validate_date(date_str: str) -> bool:
    """
    Validate that the date is within the next 7 days.
    
    Args:
        date_str: ISO date string (YYYY-MM-DD)
        
    Returns:
        True if valid, False otherwise
    """
    try:
        target_date = datetime.fromisoformat(date_str)
        today = datetime.now()
        max_date = today + timedelta(days=7)
        
        return today <= target_date <= max_date
    except ValueError:
        return False


def format_weather_response(weather_data: dict, partner_name: Optional[str] = None) -> str:
    """
    Format weather data into a conversational response.
    
    Args:
        weather_data: Weather data dictionary
        partner_name: Optional partner name for contextualized response
        
    Returns:
        Formatted weather description
    """
    location = weather_data["location"]
    temp_c = weather_data["temperature_c"]
    temp_f = weather_data["temperature_f"]
    conditions = weather_data["conditions"]
    precip = weather_data["precipitation_prob"]
    date = weather_data["date"]
    
    # Build response
    if partner_name:
        response = f"The weather in {location} for your visit to {partner_name} "
    else:
        response = f"The weather in {location} "
    
    # Add date context
    target_date = datetime.fromisoformat(date)
    today = datetime.now().date()
    
    if target_date.date() == today:
        response += "today "
    elif target_date.date() == today + timedelta(days=1):
        response += "tomorrow "
    else:
        response += f"on {target_date.strftime('%A, %B %d')} "
    
    response += f"will be {conditions} with temperatures around {temp_c}°C ({temp_f}°F). "
    
    # Add precipitation info
    if precip > 50:
        response += f"There's a {round(precip)}% chance of rain - pack an umbrella! "
    elif precip > 20:
        response += f"There's a {round(precip)}% chance of rain. "
    
    # Add temperature-based advice
    if temp_c < 5:
        response += "It will be quite cold, so dress warmly."
    elif temp_c > 30:
        response += "It will be hot, so stay hydrated and consider light clothing."
    
    return response


@tool
async def weather_forecast(location: str, date: Optional[str] = None) -> str:
    """
    Get weather forecast for a specified location and optional date.
    
    Use this tool when the user asks about weather conditions at a location.
    The location should be in format "City, Country" (e.g., "Berlin, Germany").
    
    Args:
        location: Location in format "City, Country"
        date: Optional date in ISO format (YYYY-MM-DD). Must be within next 7 days.
        
    Returns:
        A formatted weather forecast description
    """
    # Parse location
    parts = [p.strip() for p in location.split(",")]
    if len(parts) < 2:
        return f"Invalid location format. Please provide location as 'City, Country' (e.g., 'Berlin, Germany')"
    
    city = parts[0]
    country = parts[1]
    
    # Validate date if provided
    if date and not validate_date(date):
        return "Date must be within the next 7 days. Weather forecasts are only available for the next week."
    
    try:
        weather_data = await get_weather_forecast_data(city, country, date)
        return format_weather_response(weather_data)
    except WeatherAPIError as e:
        return f"Unable to retrieve weather data: {str(e)}. Please try again later."
