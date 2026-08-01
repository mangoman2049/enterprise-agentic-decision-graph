import networkx as nx
import json
import os

class KnowledgeGraphEngine:
    """
    Enterprise Decision Graph.
    Uses NetworkX to build an ontology of:
    Entity -> Policy -> Decision -> Outcome
    """
    def __init__(self):
        self.graph = nx.DiGraph()
        
    def _get_policy_node_id(self, industry: str, reasons: list) -> str:
        reason_str = ", ".join(sorted(reasons))
        return f"Policy|{industry}|{reason_str}"
        
    def record_decision(self, lead: dict, reasons: list, decision: str, outcome: str = None):
        """
        Records a human decision and (optionally) the 6-month outcome into the graph.
        Nodes added: 
        1. Entity Node (e.g. Industry:Finance)
        2. Policy Node (e.g. Missing SOC2)
        3. Decision Node (Approve/Reject)
        4. Outcome Node (Renewed/Churned)
        """
        industry = lead.get("industry", "Unknown")
        company = lead.get("company", "Unknown")
        
        entity_node = f"Entity|Industry|{industry}"
        policy_node = self._get_policy_node_id(industry, reasons)
        decision_node = f"Decision|{decision.upper()}|{policy_node}"
        
        # Add nodes with types
        self.graph.add_node(entity_node, type="Entity", label=f"Industry: {industry}")
        self.graph.add_node(policy_node, type="Policy", label=f"Escalation: {', '.join(reasons)}")
        self.graph.add_node(decision_node, type="Decision", label=f"Decision: {decision.upper()}")
        
        # Add edges
        self.graph.add_edge(entity_node, policy_node)
        
        # We track how many times this decision was made
        if self.graph.has_edge(policy_node, decision_node):
            self.graph[policy_node][decision_node]['weight'] += 1
        else:
            self.graph.add_edge(policy_node, decision_node, weight=1)
            
        # Record Outcome if provided
        if outcome:
            outcome_node = f"Outcome|{outcome.upper()}|{decision_node}"
            self.graph.add_node(outcome_node, type="Outcome", label=f"Outcome: {outcome.upper()}")
            
            if self.graph.has_edge(decision_node, outcome_node):
                self.graph[decision_node][outcome_node]['weight'] += 1
            else:
                self.graph.add_edge(decision_node, outcome_node, weight=1)
                
            # Connect the specific company to the outcome (Evidence)
            company_node = f"Entity|Company|{company}"
            self.graph.add_node(company_node, type="Entity", label=f"Company: {company}")
            self.graph.add_edge(company_node, outcome_node, label="Experienced")

    def evaluate_policy(self, lead: dict, reasons: list) -> dict:
        """
        Calculates confidence in a policy based on Historical Outcomes.
        Returns whether to Auto-Approve, Auto-Reject, or Escalate with warnings.
        """
        industry = lead.get("industry", "Unknown")
        policy_node = self._get_policy_node_id(industry, reasons)
        
        if not self.graph.has_node(policy_node):
            return {"status": "ESCALATE", "reason": "No precedent found."}
            
        # Get all decisions for this policy
        decisions = list(self.graph.successors(policy_node))
        
        approvals = 0
        rejections = 0
        renewals = 0
        churns = 0
        
        for d_node in decisions:
            weight = self.graph[policy_node][d_node]['weight']
            if "APPROVE" in d_node:
                approvals += weight
                # Check outcomes of these approvals
                outcomes = list(self.graph.successors(d_node))
                for o_node in outcomes:
                    o_weight = self.graph[d_node][o_node]['weight']
                    if "RENEWED" in o_node:
                        renewals += o_weight
                    elif "CHURNED" in o_node:
                        churns += o_weight
            elif "REJECT" in d_node:
                rejections += weight
                
        # Rule 1: Learn Mistakes (High Churn Rate on Approvals)
        total_outcomes = renewals + churns
        if total_outcomes > 0:
            churn_rate = churns / total_outcomes
            if churn_rate > 0.5:
                return {
                    "status": "ESCALATE_WARNING",
                    "reason": f"🚨 Policy Confidence Reduced! Past {approvals} approvals resulted in {churn_rate*100:.0f}% CHURN."
                }
                
        # Rule 2: Safe Auto-Approve (Consistent Approvals + Good Outcomes)
        if approvals >= 2 and churns == 0:
            return {
                "status": "AUTO_APPROVE",
                "reason": f"Precedent established ({approvals} approvals) with Zero Churn."
            }
            
        # Rule 3: Consistent Rejection
        if rejections >= 2:
            return {
                "status": "AUTO_REJECT",
                "reason": f"Precedent established ({rejections} rejections)."
            }
            
        return {"status": "ESCALATE", "reason": "Precedent established, but requires more data to auto-resolve."}
