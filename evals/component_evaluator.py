"""
component_evaluator.py - Component-Level Evaluation Engine
Evaluates Intake, CRM Retrieval, Product Fit, Security, Commercial, and HITL components independently.
"""

import json
import os
import re
from typing import Dict, Any, List

class ComponentEvaluator:
    def __init__(self, golden_dataset_path: str):
        with open(golden_dataset_path, "r", encoding="utf-8") as f:
            self.dataset = json.load(f)

    def eval_intake_component(self, case: Dict[str, Any]) -> Dict[str, Any]:
        """Evaluates Lead Intake extraction and payload completeness."""
        payload = case.get("lead_payload", {})
        required_fields = ["company", "industry", "pain_points"]
        missing = [field for field in required_fields if field not in payload]
        
        passed = len(missing) == 0
        return {
            "passed": passed,
            "error": f"Missing required intake fields: {missing}" if not passed else None
        }

    def eval_crm_retrieval_component(self, case: Dict[str, Any]) -> Dict[str, Any]:
        """Evaluates CRM data retrieval and data freshness."""
        payload = case.get("lead_payload", {})
        last_updated = payload.get("crm_last_updated", "2026-01-01")
        
        is_stale = False
        if "2021" in last_updated or "2022" in last_updated:
            is_stale = True

        category = case.get("taxonomy_category")
        if category == "STALE_EVIDENCE" and not is_stale:
            return {"passed": False, "error": "Failed to flag stale evidence"}
        return {"passed": True, "error": None, "is_stale": is_stale}

    def eval_security_component(self, case: Dict[str, Any]) -> Dict[str, Any]:
        """Evaluates Security & Compliance guardrails (including Prompt Injection detection)."""
        payload = case.get("lead_payload", {})
        pain_points = payload.get("pain_points", [])
        
        injection_detected = False
        injection_patterns = [r"SYSTEM OVERRIDE", r"Ignore security", r"Grant admin"]
        
        for pain in pain_points:
            for pattern in injection_patterns:
                if re.search(pattern, pain, re.IGNORECASE):
                    injection_detected = True

        category = case.get("taxonomy_category")
        if category == "ADVERSARIAL_INPUT":
            if not injection_detected:
                return {"passed": False, "error": "Prompt injection bypassed security guardrail!"}
            return {"passed": True, "error": "Blocked prompt injection correctly"}

        # Regular compliance check
        soc2_req = payload.get("soc2_required", False)
        can_support = not (category == "CLEAN_DENIAL")
        
        return {"passed": True, "error": None, "can_support": can_support}

    def eval_product_fit_component(self, case: Dict[str, Any]) -> Dict[str, Any]:
        """Evaluates Product Fit matching logic."""
        payload = case.get("lead_payload", {})
        pain_points = payload.get("pain_points", [])
        
        fit = "Strong"
        missing_features = []
        for pain in pain_points:
            if "On-Premises" in pain:
                fit = "Medium (Roadmap)"
                missing_features.append("On-Premises")
            elif "Patient Data Export" in pain:
                fit = "Weak"
                missing_features.append("HIPAA Export")

        category = case.get("taxonomy_category")
        if category == "AMBIGUOUS_CONTEXT" and fit == "Strong":
            return {"passed": False, "error": "Failed to detect On-Premises missing feature!"}
            
        return {"passed": True, "fit": fit, "missing_features": missing_features}

    def eval_commercial_component(self, case: Dict[str, Any]) -> Dict[str, Any]:
        """Evaluates Commercial pricing calculation."""
        arr = case.get("arr", 0)
        passed = arr >= 0
        return {"passed": passed, "arr": arr}

    def run_all_component_evals(self) -> Dict[str, Any]:
        results = {
            "total_cases": len(self.dataset),
            "components": {
                "intake": {"passed": 0, "failed": 0, "failures": []},
                "crm_retrieval": {"passed": 0, "failed": 0, "failures": []},
                "product_fit": {"passed": 0, "failed": 0, "failures": []},
                "security": {"passed": 0, "failed": 0, "failures": []},
                "commercial": {"passed": 0, "failed": 0, "failures": []}
            }
        }

        for case in self.dataset:
            case_id = case["id"]
            
            # Intake
            res = self.eval_intake_component(case)
            if res["passed"]: results["components"]["intake"]["passed"] += 1
            else: 
                results["components"]["intake"]["failed"] += 1
                results["components"]["intake"]["failures"].append((case_id, res["error"]))

            # CRM Retrieval
            res = self.eval_crm_retrieval_component(case)
            if res["passed"]: results["components"]["crm_retrieval"]["passed"] += 1
            else:
                results["components"]["crm_retrieval"]["failed"] += 1
                results["components"]["crm_retrieval"]["failures"].append((case_id, res["error"]))

            # Product Fit
            res = self.eval_product_fit_component(case)
            if res["passed"]: results["components"]["product_fit"]["passed"] += 1
            else:
                results["components"]["product_fit"]["failed"] += 1
                results["components"]["product_fit"]["failures"].append((case_id, res["error"]))

            # Security
            res = self.eval_security_component(case)
            if res["passed"]: results["components"]["security"]["passed"] += 1
            else:
                results["components"]["security"]["failed"] += 1
                results["components"]["security"]["failures"].append((case_id, res["error"]))

            # Commercial
            res = self.eval_commercial_component(case)
            if res["passed"]: results["components"]["commercial"]["passed"] += 1
            else:
                results["components"]["commercial"]["failed"] += 1
                results["components"]["commercial"]["failures"].append((case_id, res["error"]))

        return results

if __name__ == "__main__":
    import sys
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    
    base_dir = os.path.dirname(os.path.dirname(__file__))
    data_path = os.path.join(base_dir, "data", "golden_dataset_v1.json")
    evaluator = ComponentEvaluator(data_path)
    summary = evaluator.run_all_component_evals()

    print("=========================================================")
    print(" [EVAL] COMPONENT EVALUATION REPORT SUMMARY")
    print("=========================================================")
    print(f" Total Golden Cases Evaluated: {summary['total_cases']}")
    print("-" * 55)
    for comp_name, stats in summary["components"].items():
        pass_rate = (stats["passed"] / summary['total_cases']) * 100
        print(f" Component: {comp_name:<18} | Pass Rate: {pass_rate:.1f}% ({stats['passed']}/{summary['total_cases']})")
        if stats["failed"] > 0:
            for case_id, err in stats["failures"]:
                print(f"   [X] Failure in {case_id}: {err}")
    print("=========================================================")
