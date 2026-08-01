import asyncio
import json
from .base_agent import BaseAgent

class ProductFitAgent(BaseAgent):
    def __init__(self, mcp_client=None):
        super().__init__("product_fit", "Matches use cases against KB MCP.")
        self.mcp_client = mcp_client

    async def _execute(self, context: dict, span) -> dict:
        pain_points = context.get("pain_points", [])
        
        kb_result = {"fit": "Unknown", "missing_features": []}
        
        if self.mcp_client and pain_points:
            raw_result = await self.mcp_client.call_tool("check_product_fit", {"pain_points": pain_points})
            kb_result = self._parse_mcp_result(raw_result)
            
            # If missing features, check roadmap
            if kb_result.get("fit") == "Weak" and kb_result.get("missing_features"):
                missing = kb_result["missing_features"][0]
                roadmap_raw = await self.mcp_client.call_tool("check_roadmap", {"feature_name": missing})
                roadmap = self._parse_mcp_result(roadmap_raw)
                
                if roadmap.get("status") == "Planned":
                    kb_result["fit"] = "Medium (Roadmap)"
                    kb_result["roadmap_eta"] = roadmap.get("eta")
        
        span.set_attribute("product_fit", kb_result.get("fit", "Unknown"))
        
        return kb_result
        
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
