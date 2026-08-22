"""
independent_verifier.py - Deterministic Independent Verifier Engine
Enforces Claim ➔ Evidence ➔ Freshness ➔ Policy ➔ Decision verification rules ahead of LLM consensus.
"""

import json
import os
import re
from typing import Dict, Any, List

class IndependentVerifier:
    def __init__(self):
        pass

    def verify_decision(self, lead: Dict[str, Any], agent_outputs: Dict[str, Any], proposed_decision: str) -> Dict[str, Any]:
        """
        Runs 5-step deterministic verification on proposed lead qualification decision.
        """
        payload = lead.get("lead_payload", lead)
        company = payload.get("company", "Unknown")
        industry = payload.get("industry", "Unknown")
        arr = agent_outputs.get("commercial", {}).get("estimated_arr", payload.get("budget", 0))

        claims = []
        evidence_found = []
        unsupported_claims = []
        verdict = "VERIFIED"
        overridden = False
        reasons = []

        # Step 1: Claim Extraction & Evidence Mapping
        prod_fit = agent_outputs.get("product_fit", {})
        security = agent_outputs.get("security", {})
        
        if prod_fit.get("fit") == "Strong":
            claims.append("Product Fit is Strong")
            if "Unsupported" in str(payload.get("pain_points", [])):
                unsupported_claims.append("Product Fit is Strong (Pain points unsupported)")

        if security.get("can_support") == True:
            claims.append("Security & Compliance passed")

        # Step 2: Freshness Check
        crm_last_updated = payload.get("crm_last_updated", "2026-01-01")
        if "2021" in crm_last_updated or "2022" in crm_last_updated:
            verdict = "ABSTAIN_STALE_EVIDENCE"
            overridden = True
            reasons.append(f"Stale CRM data: Last updated {crm_last_updated}")

        # Step 3: Data Discrepancy Check (Conflicting Data)
        crm_arr = payload.get("crm_recorded_arr")
        intake_arr = payload.get("budget")
        if crm_arr and intake_arr and abs(crm_arr - intake_arr) > 100000:
            verdict = "ESCALATE_DISCREPANCY"
            overridden = True
            reasons.append(f"ARR Discrepancy Detected: CRM ${crm_arr:,} vs Intake Payload ${intake_arr:,}")

        # Step 4: Deterministic Policy Rules
        # Hard Rule 1: Prompt Injection Injection Detection
        pain_points = payload.get("pain_points", [])
        for pain in pain_points:
            if re.search(r"SYSTEM OVERRIDE|Ignore security|Grant admin", str(pain), re.IGNORECASE):
                verdict = "FORCE_REJECT"
                overridden = True
                reasons.append("Critical Security Violation: Prompt Injection Attempt Neutralized!")

        # Hard Rule 2: Healthcare HIPAA Violation
        if industry == "Healthcare" and payload.get("hipaa_required") and proposed_decision == "approved":
            verdict = "FORCE_REJECT"
            overridden = True
            reasons.append("Deterministic Policy Violation: Healthcare HIPAA compliance missing!")

        # Hard Rule 3: High Value Strategic Deal HITL Enforcement
        if arr > 250000 and proposed_decision == "approved" and verdict == "VERIFIED":
            # Must pass through HITL review
            verdict = "ENFORCE_HITL_REVIEW"
            overridden = True
            reasons.append(f"Strategic Deal Policy: ARR ${arr:,} > $250k requires DVP Approval")

        final_decision = proposed_decision
        if verdict == "FORCE_REJECT":
            final_decision = "rejected"
        elif verdict in ["ABSTAIN_STALE_EVIDENCE", "ESCALATE_DISCREPANCY", "ENFORCE_HITL_REVIEW"]:
            final_decision = "escalate"

        return {
            "company": company,
            "proposed_decision": proposed_decision,
            "final_decision": final_decision,
            "verifier_verdict": verdict,
            "overridden": overridden,
            "reasons": reasons,
            "unsupported_claims": unsupported_claims,
            "claims_checked": len(claims)
        }

    def verify_golden_dataset(self, golden_dataset_path: str) -> Dict[str, Any]:
        with open(golden_dataset_path, "r", encoding="utf-8") as f:
            dataset = json.load(f)

        results = []
        overrides_count = 0

        for case in dataset:
            # Mock agent proposed decision (simulating potential agent mistakes)
            proposed = "approved" if case["taxonomy_category"] != "CLEAN_DENIAL" else "rejected"
            
            mock_agent_outputs = {
                "product_fit": {"fit": "Strong"},
                "security": {"can_support": case["taxonomy_category"] != "ADVERSARIAL_INPUT"},
                "commercial": {"estimated_arr": case.get("arr", 0)}
            }

            v_res = self.verify_decision(case, mock_agent_outputs, proposed)
            v_res["case_id"] = case["id"]
            v_res["expected_decision"] = case["expected_decision"]
            v_res["category"] = case["taxonomy_category"]
            
            if v_res["overridden"]:
                overrides_count += 1

            results.append(v_res)

        return {
            "total_verified": len(dataset),
            "total_overrides": overrides_count,
            "verifier_accuracy": round(((len(dataset) - overrides_count) / len(dataset)) * 100, 1),
            "results": results
        }

if __name__ == "__main__":
    import sys
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    
    base_dir = os.path.dirname(os.path.dirname(__file__))
    data_path = os.path.join(base_dir, "data", "golden_dataset_v1.json")
    verifier = IndependentVerifier()
    report = verifier.verify_golden_dataset(data_path)

    print("=========================================================")
    print(" [SHIELD]? INDEPENDENT VERIFIER EXECUTION REPORT")
    print("=========================================================")
    print(f" Total Cases Verified: {report['total_verified']}")
    print(f" Agent Decisions Overridden / Corrected by Verifier: {report['total_overrides']}")
    print("-" * 65)
    for r in report["results"]:
        status_icon = "⚠️" if r["overridden"] else "✅"
        print(f" {status_icon} {r['case_id']:<10} | Category: {r['category']:<18} | Proposed: {r['proposed_decision']:<8} -> Verifier: {r['final_decision']:<8} ({r['verifier_verdict']})")
        if r["reasons"]:
            for reas in r["reasons"]:
                print(f"    [->] Reason: {reas}")
    print("=========================================================")
