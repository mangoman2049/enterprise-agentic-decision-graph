import asyncio
from opentelemetry import trace

from agents.lead_intake import LeadIntakeAgent
from agents.research import ResearchAgent
from agents.qualification import QualificationAgent
from agents.product_fit import ProductFitAgent
from agents.security import SecurityAgent
from agents.commercial import CommercialAgent
from hitl.human_approval import HumanApprovalAgent

tracer = trace.get_tracer("v5_enterprise_agents")

class WorkflowEngine:
    def __init__(self, crm_mcp, kb_mcp, security_mcp, knowledge_graph=None):
        self.intake = LeadIntakeAgent()
        self.research = ResearchAgent(crm_mcp)
        self.qual = QualificationAgent()
        self.product = ProductFitAgent(kb_mcp)
        self.security = SecurityAgent(security_mcp)
        self.commercial = CommercialAgent()
        self.hitl = HumanApprovalAgent(knowledge_graph)

    async def process_lead(self, lead: dict, phase: str = "P2") -> dict:
        with tracer.start_as_current_span("orchestrator.process_lead") as root_span:
            root_span.set_attribute("lead.company", lead.get("company", ""))
            
            print(f"\n🚀 Processing Lead: {lead.get('company')} ({lead.get('industry')})")
            
            intake_res = await self.intake.process(lead)
            lead.update(intake_res)
            print(f"  ✓ Intake: Urgency {intake_res.get('urgency')}")
            
            research_res = await self.research.process(lead)
            lead.update(research_res)
            
            qual_res = await self.qual.process(lead)
            
            if not qual_res.get("qualified"):
                print("  ❌ Disqualified early (Cold Lead/Low Score)")
                return {"status": "Disqualified", "reason": "Low Qual Score"}

            product_task = asyncio.create_task(self.product.process(lead))
            security_task = asyncio.create_task(self.security.process(lead))
            commercial_task = asyncio.create_task(self.commercial.process(lead))
            
            product_res, security_res, commercial_res = await asyncio.gather(
                product_task, security_task, commercial_task
            )
            
            # Orchestrator evaluates the parallel results to see if HITL is needed.
            hitl_res = await self.hitl.evaluate_escalation(
                lead, qual_res, product_res, security_res, commercial_res, phase
            )
            
            if hitl_res.get("requires_human"):
                if hitl_res.get("decision") == "rejected":
                    return {"status": "Disqualified", "reason": "Rejected by Human/Graph"}
                else:
                    status_msg = "Qualified (Auto-Approved by Brain)" if hitl_res.get("auto_override") else "Qualified (Approved by Human)"
                    return {"status": status_msg, "arr": commercial_res.get('estimated_arr')}
            
            return {"status": "Auto-Qualified", "arr": commercial_res.get('estimated_arr')}
