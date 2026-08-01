from fastmcp import FastMCP

mcp = FastMCP("Security Server")

@mcp.tool()
def check_compliance_posture(company_name: str, country: str, industry: str, soc2_required: bool) -> dict:
    """Evaluates if we can meet the security compliance requirements."""
    
    issues = []
    
    # We mock that we don't have EU Data Residency yet
    if country in ["UK", "DE"]:
        issues.append("GDPR Data Residency: EU region deployment required (Not supported yet)")
        
    # We mock that our SOC2 audit is slightly out of date (13 months)
    if soc2_required:
        issues.append("SOC2: Audit is 13 months old (Warning)")
        
    if industry == "Healthcare":
        issues.append("HIPAA: BAA signing required")
        
    can_support = len(issues) < 2  # Arbitrary rule for simulation
    
    return {
        "can_support": can_support,
        "issues": issues,
        "certifications": ["SOC2 Type II (Expired last month)", "ISO 27001"]
    }

if __name__ == "__main__":
    mcp.run(transport="stdio")
