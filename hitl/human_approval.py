import asyncio
import sys
import uuid
from opentelemetry import trace

tracer = trace.get_tracer("v5_enterprise_agents")

# Global state for Web UI
hitl_queue = {}
metrics = {
    "total_pipeline": 0,
    "auto_approved": 0,
    "auto_rejected": 0,
    "manual_approved": 0,
    "manual_rejected": 0,
}

class HumanApprovalAgent:
    def __init__(self, knowledge_graph=None):
        self.name = "human_approval"
        self.graph = knowledge_graph
        
    async def evaluate_escalation(self, lead: dict, qualification: dict, 
                                  product: dict, security: dict, commercial: dict, phase: str = "P2") -> dict:
        """Determines if a human needs to review based on policies."""
        
        reasons = []
        
        if qualification.get("confidence", 100) < 85:
            reasons.append("Confidence < 85%")
        if commercial.get("estimated_arr", 0) > 250000:
            reasons.append("Deal > $250k (Strategic)")
        if not security.get("can_support", True):
            reasons.append(f"Security Blocker: {security.get('issues', [])}")
        if product.get("fit") in ["Weak", "Medium (Roadmap)"]:
            reasons.append(f"Suboptimal Product Fit: {product.get('missing_features', [])}")
            
        if not reasons:
            return {"requires_human": False}
            
        graph_warning = None
        # ─── V5 ENTERPRISE KNOWLEDGE LAYER CHECK ───
        if self.graph:
            eval_res = self.graph.evaluate_policy(lead, reasons)
            status = eval_res.get("status")
            graph_reason = eval_res.get("reason")
            
            if status == "AUTO_APPROVE":
                metrics["auto_approved"] += 1
                metrics["total_pipeline"] += commercial.get("estimated_arr", 0)
                return {
                    "requires_human": True,
                    "decision": "approved",
                    "reasons": reasons,
                    "auto_override": True
                }
            elif status == "AUTO_REJECT":
                metrics["auto_rejected"] += 1
                return {
                    "requires_human": True,
                    "decision": "rejected",
                    "reasons": reasons,
                    "auto_override": True
                }
            elif status == "ESCALATE_WARNING":
                graph_warning = graph_reason
                
        # ─── FALLBACK TO HUMAN ───
        with tracer.start_as_current_span("agent.human_approval") as span:
            span.set_attribute("hitl.reasons", str(reasons))
            
            # If in Phase 1 (Training), we simulate the human to save time.
            if phase == "P1":
                if lead.get("industry") == "Healthcare":
                    decision = "rejected"
                    metrics["manual_rejected"] += 1
                else:
                    decision = "approved"
                    metrics["manual_approved"] += 1
                    metrics["total_pipeline"] += commercial.get("estimated_arr", 0)
            else:
                # Real human in Phase 2 via Web UI
                hitl_id = str(uuid.uuid4())
                fut = asyncio.Future()
                
                # Add to web queue
                hitl_queue[hitl_id] = {
                    "future": fut,
                    "lead": lead,
                    "commercial": commercial,
                    "security": security,
                    "product": product,
                    "reasons": reasons,
                    "graph_warning": graph_warning
                }
                
                # Suspend workflow engine for this lead until web UI posts decision
                decision = await fut
            
            span.set_attribute("hitl.decision", decision)
            
            # ─── RECORD DECISION & OUTCOME TO GRAPH ───
            if self.graph:
                outcome = lead.get("_simulated_outcome") if phase == "P1" else None
                self.graph.record_decision(lead, reasons, decision, outcome)
            
            return {
                "requires_human": True,
                "decision": decision,
                "reasons": reasons,
                "auto_override": False
            }
