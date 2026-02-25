"""Business Partner Lookup Tool

This tool searches for business partners by name using fuzzy matching.
Uses mock data for development (to be replaced with real S/4HANA OData integration).
"""

from typing import Optional
from langchain_core.tools import tool

# Mock business partner data with diverse global locations
MOCK_PARTNERS = [
    {"id": "BP001", "name": "Acme Corp", "city": "New York", "country": "USA"},
    {"id": "BP002", "name": "TechVentures GmbH", "city": "Berlin", "country": "Germany"},
    {"id": "BP003", "name": "Global Innovations Ltd", "city": "London", "country": "UK"},
    {"id": "BP004", "name": "Pacific Solutions", "city": "Tokyo", "country": "Japan"},
    {"id": "BP005", "name": "Nordic Systems AB", "city": "Stockholm", "country": "Sweden"},
    {"id": "BP006", "name": "Alpine Technologies SA", "city": "Zurich", "country": "Switzerland"},
    {"id": "BP007", "name": "Southern Cross Enterprises", "city": "Sydney", "country": "Australia"},
    {"id": "BP008", "name": "Maple Leaf Industries", "city": "Toronto", "country": "Canada"},
    {"id": "BP009", "name": "Dragon Tech Co", "city": "Shanghai", "country": "China"},
    {"id": "BP010", "name": "Sunset Digital", "city": "San Francisco", "country": "USA"},
]


def search_business_partner(partner_name: str) -> Optional[dict]:
    """
    Search for a business partner by name using fuzzy matching.
    
    Args:
        partner_name: Name or partial name of the business partner to search for
        
    Returns:
        Dictionary with partner info (id, name, city, country) or None if not found
    """
    if not partner_name:
        return None
    
    # Normalize search term (lowercase, strip whitespace)
    search_term = partner_name.lower().strip()
    
    # Try exact match first (case-insensitive)
    for partner in MOCK_PARTNERS:
        if partner["name"].lower() == search_term:
            return partner
    
    # Try partial match (case-insensitive)
    for partner in MOCK_PARTNERS:
        if search_term in partner["name"].lower():
            return partner
    
    # No match found
    return None


@tool
def business_partner_lookup(partner_name: str) -> str:
    """
    Look up a business partner by name and return their location information.
    
    Use this tool when the user asks about a business partner's location or
    wants to get weather information for a partner's location.
    
    Args:
        partner_name: The name of the business partner to look up
        
    Returns:
        A string describing the partner's location, or an error message if not found
    """
    partner = search_business_partner(partner_name)
    
    if partner:
        return (
            f"Found business partner: {partner['name']} (ID: {partner['id']}). "
            f"Location: {partner['city']}, {partner['country']}"
        )
    else:
        # Suggest alternatives by showing similar names
        suggestions = []
        search_term = partner_name.lower().strip()
        for p in MOCK_PARTNERS:
            # Find partners that share at least one word
            if any(word in p["name"].lower() for word in search_term.split()):
                suggestions.append(p["name"])
        
        if suggestions:
            return (
                f"Business partner '{partner_name}' not found. "
                f"Did you mean one of these? {', '.join(suggestions[:3])}"
            )
        else:
            return (
                f"Business partner '{partner_name}' not found. "
                f"Please check the spelling or try a different name."
            )
