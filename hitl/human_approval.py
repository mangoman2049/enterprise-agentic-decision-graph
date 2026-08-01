import asyncio
import sys
from opentelemetry import trace

tracer = trace.get_tracer("v5_enterprise_agents")

class HumanApprovalAgent:
    def __init__(self, knowledge_graph=None):
        self.name = "human_approval"
        self.graph = knowledge_graph
        
    async def evaluate_escalation(self, lead: dict, qualification: dict, 
                                  product: dict, security: dict, commercial: dict, phase: str = "P2") -> dict:
        """Determines if a human needs to review based on policies."""
        
        reasons = []
        
        # Policy 1: Low Confidence
        if qualification.get("confidence", 100) < 85:
            reasons.append("Confidence < 85%")
            
        # Policy 2: High Value Deal
        if commercial.get("estimated_arr", 0) > 250000:
            reasons.append("Deal > $250k (Strategic)")
            
        # Policy 3: Missing Compliance
        if not security.get("can_support", True):
            reasons.append(f"Security Blocker: {security.get('issues', [])}")
            
        # Policy 4: Product Fit
        if product.get("fit") in ["Weak", "Medium (Roadmap)"]:
            reasons.append(f"Suboptimal Product Fit: {product.get('missing_features', [])}")
            
        if not reasons:
            return {"requires_human": False}
            
        # ─── V5 ENTERPRISE KNOWLEDGE LAYER CHECK ───
        if self.graph:
            eval_res = self.graph.evaluate_policy(lead, reasons)
            status = eval_res.get("status")
            graph_reason = eval_res.get("reason")
            
            if status == "AUTO_APPROVE":
                print("\n" + "🧠 " * 15)
                print("  ENTERPRISE KNOWLEDGE LAYER OVERRIDE")
                print("🧠 " * 15)
                print(f"  Company: {lead.get('company')} ({lead.get('industry')})")
                print(f"  {graph_reason}")
                print(f"  Decision Auto-Applied: APPROVED")
                return {
                    "requires_human": True,
                    "decision": "approved",
                    "reasons": reasons,
                    "auto_override": True
                }
            elif status == "AUTO_REJECT":
                print("\n" + "🧠 " * 15)
                print("  ENTERPRISE KNOWLEDGE LAYER OVERRIDE")
                print("🧠 " * 15)
                print(f"  Company: {lead.get('company')} ({lead.get('industry')})")
                print(f"  {graph_reason}")
                print(f"  Decision Auto-Applied: REJECTED")
                return {
                    "requires_human": True,
                    "decision": "rejected",
                    "reasons": reasons,
                    "auto_override": True
                }
            elif status == "ESCALATE_WARNING":
                # Fall through to human, but with a dire warning from the graph
                print("\n" + "🚨 " * 15)
                print("  ENTERPRISE KNOWLEDGE LAYER WARNING")
                print(f"  {graph_reason}")
                print("🚨 " * 15)
                
        # ─── FALLBACK TO HUMAN ───
        with tracer.start_as_current_span("agent.human_approval") as span:
            span.set_attribute("hitl.reasons", str(reasons))
            
            print("\n" + "🔔 " * 15)
            print("  HUMAN-IN-THE-LOOP ESCALATION")
            print("🔔 " * 15)
            print(f"\n  🏢 Company: {lead.get('company')}")
            print(f"  💰 ARR: ${commercial.get('estimated_arr', 0):,}")
            print(f"  🔒 Security: {'PASS' if security.get('can_support') else 'FAIL'}")
            print(f"  📦 Prod Fit: {product.get('fit')}")
            print(f"\n  ⚡ Escalation Reasons:")
            for r in reasons:
                print(f"     • {r}")
                
            # If in Phase 1 (Training), we simulate the human to save time.
            if phase == "P1":
                # Simulated Human Strategy:
                # Approves almost everything (causing the churn mistake for Tech)
                # Rejects Healthcare due to strict GDPR fear.
                if lead.get("industry") == "Healthcare":
                    decision = "rejected"
                    print("  [Simulated Phase 1 Human] -> REJECTED")
                else:
                    decision = "approved"
                    print("  [Simulated Phase 1 Human] -> APPROVED")
            else:
                # Real human in Phase 2
                print("\n  ┌─────────────────────────────────────┐")
                print("  │  [A] Approve       — Override/Accept│")
                print("  │  [R] Reject        — Disqualify     │")
                print("  └─────────────────────────────────────┘")
                
                loop = asyncio.get_event_loop()
                decision = await loop.run_in_executor(None, self._get_input)
            
            span.set_attribute("hitl.decision", decision)
            
            # ─── RECORD DECISION & OUTCOME TO GRAPH ───
            if self.graph:
                # In Phase 1, we simulate time passing instantly and record the outcome
                outcome = lead.get("_simulated_outcome") if phase == "P1" else None
                self.graph.record_decision(lead, reasons, decision, outcome)
            
            return {
                "requires_human": True,
                "decision": decision,
                "reasons": reasons,
                "auto_override": False
            }
            
    def _get_input(self):
        try:
            val = input("  Your decision [A/R]: ").strip().upper()
            if val == 'A':
                print("  ✅ Decision recorded: APPROVED")
                return "approved"
            else:
                print("  ❌ Decision recorded: REJECTED")
                return "rejected"
        except (EOFError, KeyboardInterrupt):
            print("  ❌ Defaulting to REJECTED due to EOF")
            return "rejected"
