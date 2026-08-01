import asyncio
from .base_agent import BaseAgent

class LeadIntakeAgent(BaseAgent):
    def __init__(self):
        super().__init__("lead_intake", "Extracts intent and validates raw data.")

    async def _execute(self, context: dict, span) -> dict:
        await asyncio.sleep(0.1) # Simulate think time
        
        # Determine Urgency
        urgency = "Low"
        if "1 month" in context.get("timeline", "") or "3 months" in context.get("timeline", ""):
            urgency = "High"
            
        span.set_attribute("extracted.urgency", urgency)
        
        return {
            "intent": "Interested in GenAI",
            "urgency": urgency,
            "normalized_company": context.get("company", "").strip().title(),
            "valid_email": True
        }
