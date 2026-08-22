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
def search_company_news_and_stock(company_name: str) -> dict:
    """Live web search for recent company news, stock performance, and solvency events."""
    name_lower = company_name.lower()
    
    if any(k in name_lower for k in ["legacysoft", "insolvai", "chapter 11", "bankrupt", "liquidat"]):
        return {
            "company": company_name,
            "stock_trend": "DOWN_88PCT",
            "solvency_status": "BANKRUPTCY_FILED",
            "recent_headline": f"{company_name} files for Chapter 11 bankruptcy restructuring amid liquidity crisis",
            "risk_signal": "CRITICAL_FINANCIAL_DISTRESS",
            "governance_recommendation": "AUTO_REJECT_INSOLVENCY"
        }
    elif any(k in name_lower for k in ["cloudscale", "quantum", "codepilot", "acquired", "series c", "merger"]):
        return {
            "company": company_name,
            "stock_trend": "UP_22PCT",
            "solvency_status": "STRONG_GROWTH",
            "recent_headline": f"{company_name} secures $45M growth round and strategic enterprise expansion",
            "risk_signal": "HIGH_VALUE_OPPORTUNITY",
            "governance_recommendation": "STRATEGIC_UPSELL_PRIORITY"
        }
    
    return {
        "company": company_name,
        "stock_trend": "STABLE_UP_3PCT",
        "solvency_status": "SOLVENT",
        "recent_headline": f"{company_name} reports steady enterprise operational quarterly results",
        "risk_signal": "STANDARD_RISK",
        "governance_recommendation": "PROCEED_STANDARD_QUALIFICATION"
    }

if __name__ == "__main__":
    # We use stdio for the agent to call this server
    mcp.run(transport="stdio")

