"""Business Partner Lookup Tool

This tool searches for business partners using the Ariba MCP server.
Connects to the MCP server to retrieve real business partner data.
"""

import os
import httpx
from typing import Optional
from langchain_core.tools import tool

# MCP Server configuration
MCP_SERVER_URL = os.getenv(
    "ARIBA_MCP_SERVER_URL", 
    "https://mcp-server-demo-igor-dev.c-127c9ef.stage.kyma.ondemand.com/mcp/ariba"
)


async def search_business_partner_mcp(partner_name: str) -> Optional[dict]:
    """
    Search for a business partner using the Ariba MCP server.
    
    Args:
        partner_name: Name or partial name of the business partner to search for
        
    Returns:
        Dictionary with partner info or None if not found
    """
    if not partner_name:
        return None
    
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            # Call the MCP server to search for business partners
            response = await client.post(
                f"{MCP_SERVER_URL}/search",
                json={
                    "query": partner_name,
                    "limit": 1
                },
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                data = response.json()
                if data and len(data) > 0:
                    partner = data[0]
                    # Extract relevant fields
                    return {
                        "id": partner.get("id", ""),
                        "name": partner.get("name", ""),
                        "city": partner.get("city", ""),
                        "country": partner.get("country", "")
                    }
            
            return None
            
    except Exception as e:
        # Log error but don't fail - return None to indicate not found
        print(f"Error searching MCP server: {e}")
        return None


@tool
async def business_partner_lookup(partner_name: str) -> str:
    """
    Look up a business partner by name using the Ariba MCP server and return their location information.
    
    Use this tool when the user asks about a business partner's location or
    wants to get weather information for a partner's location.
    
    Args:
        partner_name: The name of the business partner to look up
        
    Returns:
        A string describing the partner's location, or an error message if not found
    """
    partner = await search_business_partner_mcp(partner_name)
    
    if partner:
        return (
            f"Found business partner: {partner['name']} (ID: {partner['id']}). "
            f"Location: {partner['city']}, {partner['country']}"
        )
    else:
        return (
            f"Business partner '{partner_name}' not found in the Ariba system. "
            f"Please check the spelling or try a different name."
        )
