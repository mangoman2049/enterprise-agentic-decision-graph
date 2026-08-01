from fastmcp import FastMCP

mcp = FastMCP("CRM Server")

@mcp.tool()
def lookup_account(company_name: str) -> dict:
    """Mock CRM lookup for an account."""
    # In a real scenario, this would query Salesforce/Hubspot via API.
    # For simulation, we return deterministic mock data.
    return {
        "account_name": company_name,
        "status": "Prospect",
        "last_contact": "2023-10-01",
        "account_owner": "Unassigned"
    }

@mcp.tool()
def get_past_opportunities(company_name: str) -> dict:
    """Look up past closed-lost or closed-won opportunities."""
    if "Microsoft" in company_name:
        return {"past_opps": 3, "status": "Closed Won", "total_value": 5000000}
    if "LocalPlumber" in company_name:
        return {"past_opps": 1, "status": "Closed Lost", "reason": "Too expensive"}
    return {"past_opps": 0, "status": "None"}

if __name__ == "__main__":
    # We use stdio for the agent to call this server
    mcp.run(transport="stdio")
