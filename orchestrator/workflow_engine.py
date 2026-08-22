"""
NOTCRM: Multi-Agent DAG Workflow Engine

Architectural Principles (AGENTS.md):
- Keep components modular and concerns clearly separated (Rule 4).
- Choose the simplest implementation that fully meets requirements (Rule 2).
- Grow the system in layers (Rule 3).
"""

import asyncio
from typing import Dict, Any, Optional
from opentelemetry import trace

from agents.lead_intake import LeadIntakeAgent
from agents.research import ResearchAgent
from agents.qualification import QualificationAgent
from agents.product_fit import ProductFitAgent
from agents.security import SecurityAgent
from agents.commercial import CommercialAgent
from hitl.human_approval import HumanApprovalAgent

tracer = trace.get_tracer("notcrm.orchestrator")

class WorkflowEngine:
    """
    Orchestrates the 7-agent DAG execution pipeline for sales lead qualification:
    
    Pipeline Topology:
    1. IntakeAgent (Sequential - Normalization)
    2. ResearchAgent (Sequential - FastMCP CRM enrichment)
    3. QualificationAgent (Sequential - Early exit thresholding)
    4. [ProductFitAgent ∥ SecurityAgent ∥ CommercialAgent] (Parallel DAG Fan-Out via asyncio.gather)
    5. HumanApprovalAgent (Sequential - Knowledge Graph & Escalation Decision Gate)
    """
    def __init__(self, crm_mcp: Any, kb_mcp: Any, security_mcp: Any, knowledge_graph: Optional[Any] = None) -> None:
        self.intake = LeadIntakeAgent()
        self.research = ResearchAgent(crm_mcp)
        self.qual = QualificationAgent()
        self.product = ProductFitAgent(kb_mcp)
        self.security = SecurityAgent(security_mcp)
        self.commercial = CommercialAgent()
        self.hitl = HumanApprovalAgent(knowledge_graph)

    async def process_lead(self, lead: Dict[str, Any], phase: str = "P2") -> Dict[str, Any]:
        """
        Processes an incoming lead through the multi-agent DAG pipeline.
        Returns final qualification result dictionary.
        """
        company_name = lead.get("company", "Unknown")
        industry = lead.get("industry", "Unknown")
        
        with tracer.start_as_current_span("orchestrator.process_lead") as root_span:
            root_span.set_attribute("lead.company", company_name)
            root_span.set_attribute("lead.industry", industry)
            root_span.set_attribute("lead.phase", phase)
            
            print(f"\n[>] Processing Lead: {company_name} ({industry}) [Phase: {phase}]")
            
            # Step 1: Lead Intake & Normalization
            intake_res = await self.intake.process(lead)
            lead.update(intake_res)
            print(f"  [OK] Intake Agent: Urgency={intake_res.get('urgency')}")
            
            # Step 2: CRM Enrichment via FastMCP
            research_res = await self.research.process(lead)
            lead.update(research_res)
            print(f"  [OK] Research Agent: CRM Status={research_res.get('crm_status')}")
            
            # Step 3: Qualification & Early Exit Check (Fail-Fast Pattern)
            qual_res = await self.qual.process(lead)
            if not qual_res.get("qualified", False):
                print(f"  [X] Disqualified Early by Qualification Agent (Score: {qual_res.get('score', 0)}/100)")
                root_span.set_attribute("qualification.early_exit", True)
                return {"status": "Disqualified", "reason": "Cold Lead / Firmographic Fit Below Threshold"}

            # Step 4: Parallel Fan-Out (Product Fit // Security // Commercial)
            # AGENTS.md Rule 4: Independent evaluations execute concurrently using asyncio.gather()
            product_task = asyncio.create_task(self.product.process(lead))
            security_task = asyncio.create_task(self.security.process(lead))
            commercial_task = asyncio.create_task(self.commercial.process(lead))
            
            product_res, security_res, commercial_res = await asyncio.gather(
                product_task, security_task, commercial_task
            )
            print(f"  [||] Parallel DAG Fan-Out Completed: Fit={product_res.get('fit')}, Security={security_res.get('can_support')}, ARR=${commercial_res.get('estimated_arr', 0):,}")
            
            # Step 5: HITL Gate & Knowledge Graph Memory Evaluation
            hitl_res = await self.hitl.evaluate_escalation(
                lead, qual_res, product_res, security_res, commercial_res, phase
            )
            
            if hitl_res.get("requires_human", False):
                if hitl_res.get("decision") == "rejected":
                    return {"status": "Disqualified", "reason": "Rejected by Governance Gate / Knowledge Graph Precedent"}
                else:
                    status_msg = "Qualified (Auto-Approved by Brain)" if hitl_res.get("auto_override") else "Qualified (Approved by DVP)"
                    return {"status": status_msg, "arr": commercial_res.get("estimated_arr", 0)}
            
            return {"status": "Auto-Qualified", "arr": commercial_res.get("estimated_arr", 0)}
