import json
import os

class ContextGraphEngine:
    """
    A lightweight Graph Engine to capture 'institutional memory'.
    It maps a specific context (Industry + Conflict Reasons) to historical Human Decisions.
    Once a threshold of precedent is reached, the graph issues an Organizational Veto,
    bypassing human approval entirely.
    """
    def __init__(self, threshold=2):
        self.threshold = threshold
        self.memory = {}
        # Pre-seed the graph with a known corporate policy ("unwritten rule")
        self.memory["Healthcare | Security Blocker: ['GDPR Data Residency: EU region deployment required (Not supported yet)']"] = {
            "approved": 0,
            "rejected": 5 # We never do this
        }

    def _make_key(self, lead: dict, reasons: list) -> str:
        # Sort reasons so the key is deterministic regardless of order
        reason_str = ", ".join(sorted(reasons))
        return f"{lead.get('industry', 'Unknown')} | {reason_str}"

    def record_decision(self, lead: dict, reasons: list, decision: str):
        """Records a human's decision into the context graph, strengthening the edge."""
        key = self._make_key(lead, reasons)
        if key not in self.memory:
            self.memory[key] = {"approved": 0, "rejected": 0}
            
        self.memory[key][decision] += 1
        
    def evaluate_precedent(self, lead: dict, reasons: list) -> dict:
        """
        Checks if the Graph has strong enough precedent to auto-resolve the conflict.
        Returns {"has_precedent": True, "decision": "approved"/"rejected"} or False.
        """
        key = self._make_key(lead, reasons)
        node = self.memory.get(key, {"approved": 0, "rejected": 0})
        
        if node["approved"] >= self.threshold:
            return {"has_precedent": True, "decision": "approved", "confidence": node["approved"]}
        if node["rejected"] >= self.threshold:
            return {"has_precedent": True, "decision": "rejected", "confidence": node["rejected"]}
            
        return {"has_precedent": False}
        
    def export_graph_data(self, filepath: str):
        """Dumps the learned context graph for visualization."""
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(self.memory, f, indent=4)
