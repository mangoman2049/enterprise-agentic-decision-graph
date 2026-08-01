import asyncio
import json
from .base_agent import BaseAgent

class SecurityAgent(BaseAgent):
    def __init__(self, mcp_client=None):
        super().__init__("security", "Evaluates compliance via Security MCP.")
        self.mcp_client = mcp_client

    async def _execute(self, context: dict, span) -> dict:
        sec_needs = context.get("security_needs", {})
        
        sec_result = {"can_support": True, "issues": []}
        
        if self.mcp_client:
            raw_result = await self.mcp_client.call_tool("check_compliance_posture", {
                "company_name": context.get("company", ""),
                "country": context.get("country", ""),
                "industry": context.get("industry", ""),
                "soc2_required": sec_needs.get("soc2_required", False)
            })
            sec_result = self._parse_mcp_result(raw_result)
            
        span.set_attribute("security_passed", sec_result.get("can_support", False))
        
        return sec_result
        
    def _parse_mcp_result(self, result) -> dict:
        if hasattr(result, "content"):
            items = result.content if isinstance(result.content, list) else [result.content]
            for item in items:
                if hasattr(item, "text"):
                    try:
                        return json.loads(item.text)
                    except:
                        pass
        return {}
