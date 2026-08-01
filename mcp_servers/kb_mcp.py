from fastmcp import FastMCP

mcp = FastMCP("Knowledge Base Server")

@mcp.tool()
def check_product_fit(pain_points: list[str]) -> dict:
    """Checks if our product solves the provided pain points."""
    unsupported = []
    supported = []
    
    for pain in pain_points:
        if "On-Premises" in pain:
            unsupported.append(pain)
        else:
            supported.append(pain)
            
    fit_score = "Strong"
    if len(unsupported) > 0:
        fit_score = "Weak"
    elif len(supported) == 0:
        fit_score = "Unknown"
        
    return {
        "fit": fit_score,
        "supported_features": supported,
        "missing_features": unsupported
    }

@mcp.tool()
def check_roadmap(feature_name: str) -> dict:
    """Checks the product roadmap for a specific feature."""
    if "On-Premises" in feature_name:
        return {"status": "Planned", "eta": "Q4 2026", "confidence": "Medium"}
    return {"status": "Not Planned"}

if __name__ == "__main__":
    mcp.run(transport="stdio")
