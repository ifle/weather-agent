"""Business Partner Lookup Tool

This tool searches for business partners using the Ariba MCP server.
The LLM will call the MCP server tools directly.
"""

import os
from typing import Optional
from langchain_core.tools import tool


# MCP Server configuration
MCP_SERVER_URL = os.getenv(
    "ARIBA_MCP_SERVER_URL", 
    "https://mcp-server-demo-igor-dev.c-127c9ef.stage.kyma.ondemand.com/mcp/ariba"
)


@tool
def business_partner_lookup(partner_name: str) -> str:
    """
    Look up a business partner by name using the Ariba MCP server.
    
    This tool provides access to the Ariba MCP server which contains business partner
    information including location data.
    
    Args:
        partner_name: The name of the business partner to look up
        
    Returns:
        Instructions for the LLM to call the MCP server tool directly
    """
    # Return instruction for the LLM to use MCP tools
    return (
        f"To look up business partner '{partner_name}', you should use the MCP server tools directly. "
        f"The Ariba MCP server is available at: {MCP_SERVER_URL}. "
        f"Use the MCP tools to search for the partner and retrieve their location information."
    )
