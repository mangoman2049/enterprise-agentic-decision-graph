import asyncio
from .base_agent import BaseAgent

class QualificationAgent(BaseAgent):
    def __init__(self):
        super().__init__("qualification", "Applies BANT scoring to determine confidence.")

    async def _execute(self, context: dict, span) -> dict:
        await asyncio.sleep(0.1)
        
        score = 0
        
        # B: Budget
        has_budget = context.get("budget") is not None
        if has_budget: score += 25
            
        # A: Authority (mocked based on employee size vs budget)
        has_authority = context.get("raw_employees", 0) < 1000 or has_budget
        if has_authority: score += 25
            
        # N: Need (pain points exist)
        if len(context.get("pain_points", [])) > 0: score += 25
            
        # T: Timing
        timeline = context.get("timeline", "")
        if "1 month" in timeline or "3 months" in timeline: score += 25
        elif "6 months" in timeline: score += 10
        
        span.set_attribute("bant_score", score)
        
        return {
            "confidence": score,
            "qualified": score >= 50
        }
