import asyncio
from .base_agent import BaseAgent

class ResearchAgent(BaseAgent):
    def __init__(self, mcp_client=None):
        super().__init__("researcher", "Enriches lead with CRM and public data.")
        self.mcp_client = mcp_client

    async def _execute(self, context: dict, span) -> dict:
        company = context.get("company", "")
        
        # Call CRM MCP to see if they are an existing account
        crm_data = {}
        if self.mcp_client:
            crm_result = await self.mcp_client.call_tool("lookup_account", {"company_name": company})
            # Parse MCP result
            crm_data = self._parse_mcp_result(crm_result)
            span.add_event("crm_lookup", attributes={"status": crm_data.get("status", "Unknown")})
            
        await asyncio.sleep(0.2)
        
        return {
            "crm_status": crm_data.get("status", "New Prospect"),
            "enriched_revenue": context.get("raw_revenue", 0),
            "enriched_employees": context.get("raw_employees", 0)
        }
        
    def _parse_mcp_result(self, result) -> dict:
        if hasattr(result, "content"):
            import json
            items = result.content if isinstance(result.content, list) else [result.content]
            for item in items:
                if hasattr(item, "text"):
                    try:
                        return json.loads(item.text)
                    except:
                        pass
        return {}
