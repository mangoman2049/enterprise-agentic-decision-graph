import asyncio
from .base_agent import BaseAgent

class CommercialAgent(BaseAgent):
    def __init__(self):
        super().__init__("commercial", "Calculates Estimated ARR and Risk.")

    async def _execute(self, context: dict, span) -> dict:
        await asyncio.sleep(0.1)
        
        employees = context.get("raw_employees", 0)
        budget = context.get("budget")
        
        # Simple ARR calc: $100 per employee, capped by budget if budget exists
        estimated_arr = employees * 100
        if budget is not None:
            estimated_arr = min(estimated_arr, budget)
            
        # Risk assessment
        risk = "Low"
        if estimated_arr > 250000:
            risk = "High"
            
        span.set_attribute("estimated_arr", estimated_arr)
        
        return {
            "estimated_arr": estimated_arr,
            "margin": "85%",
            "risk": risk
        }
