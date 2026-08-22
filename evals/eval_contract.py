"""
eval_contract.py - Evaluation Contract Definition & Validator Engine
Defines the 4 core metric classes and enforces quality/governance thresholds.
"""

from typing import Dict, Any, List

METRIC_CONTRACTS = {
    "business_outcome": {
        "decision_accuracy": {"target": 0.92, "unit": "%", "owner": "DVP Sales Ops", "critical": True},
        "churn_prevention_rate": {"target": 0.95, "unit": "%", "owner": "Head of CS", "critical": True},
        "revenue_preservation_ratio": {"target": 0.90, "unit": "%", "owner": "VP Revenue Strategy", "critical": False}
    },
    "agent_quality": {
        "schema_compliance": {"target": 1.00, "unit": "%", "owner": "AI Lead Eng", "critical": True},
        "claim_groundedness": {"target": 1.00, "unit": "%", "owner": "Verification Eng", "critical": True},
        "tool_calling_accuracy": {"target": 0.98, "unit": "%", "owner": "Platform Architect", "critical": False}
    },
    "system_performance": {
        "p95_latency_sec": {"target": 2.50, "unit": "sec", "owner": "PRE", "critical": False},
        "token_efficiency": {"target": 0.85, "unit": "%", "owner": "AI Platform Architect", "critical": False},
        "cost_per_deal_usd": {"target": 0.15, "unit": "USD", "owner": "AI Commercial Leader", "critical": False}
    },
    "governance_safety": {
        "unsupported_claim_rate": {"target": 0.00, "unit": "%", "owner": "Chief Risk Officer", "critical": True},
        "high_risk_false_approval_rate": {"target": 0.00, "unit": "%", "owner": "VP Security", "critical": True},
        "policy_sequence_integrity": {"target": 1.00, "unit": "%", "owner": "Governance Lead", "critical": True}
    }
}

class EvalContractEngine:
    def __init__(self):
        self.contracts = METRIC_CONTRACTS

    def evaluate_metrics(self, measured_metrics: Dict[str, float]) -> Dict[str, Any]:
        """Compares measured metrics against contract targets and identifies violations."""
        results = []
        violations = []
        all_passed = True

        for category, metrics in self.contracts.items():
            for metric_name, spec in metrics.items():
                val = measured_metrics.get(metric_name)
                if val is None:
                    continue

                target = spec["target"]
                unit = spec["unit"]
                critical = spec["critical"]

                # Check pass condition
                passed = True
                if "rate" in metric_name or "latency" in metric_name or "cost" in metric_name:
                    if metric_name in ["churn_prevention_rate", "revenue_preservation_ratio", "decision_accuracy", "schema_compliance", "claim_groundedness", "tool_calling_accuracy", "token_efficiency", "policy_sequence_integrity"]:
                        passed = val >= target
                    else: # lower is better (unsupported_claim_rate, high_risk_false_approval_rate, latency, cost)
                        passed = val <= target
                else:
                    passed = val >= target

                if not passed:
                    all_passed = False
                    if critical:
                        violations.append({
                            "category": category,
                            "metric": metric_name,
                            "measured": val,
                            "target": target,
                            "owner": spec["owner"],
                            "critical": True
                        })

                results.append({
                    "category": category,
                    "metric": metric_name,
                    "measured": val,
                    "target": target,
                    "unit": unit,
                    "passed": passed,
                    "critical": critical,
                    "owner": spec["owner"]
                })

        return {
            "all_passed": all_passed,
            "total_evaluated": len(results),
            "critical_violations": len(violations),
            "metrics": results,
            "violations": violations
        }

if __name__ == "__main__":
    engine = EvalContractEngine()
    test_metrics = {
        "decision_accuracy": 0.94,
        "churn_prevention_rate": 0.91, # Violation!
        "schema_compliance": 1.00,
        "claim_groundedness": 0.95, # Violation!
        "unsupported_claim_rate": 0.05, # Violation!
        "p95_latency_sec": 1.80
    }
    report = engine.evaluate_metrics(test_metrics)
    print("Contract Evaluation Summary:")
    print(f"Passed: {report['all_passed']} | Critical Violations: {report['critical_violations']}")
    for v in report['violations']:
        print(f" [!] Violation: {v['metric']} = {v['measured']} (Target: {v['target']}) - Owner: {v['owner']}")
