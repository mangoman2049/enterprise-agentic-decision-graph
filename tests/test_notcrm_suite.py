"""
NOTCRM - Comprehensive Automated Test Suite
===========================================
Executes 36 automated test scenarios across all 10 core subsystems:
1. Multi-Session Concurrency & State Isolation
2. Vertical Dataset Switching & Schema Integrity
3. Operational DVP Command Center & HITL Decision Lifecycle
4. Foundation Architecture Lab (F1-F4)
5. Evals & Verification Suite (E1-E6)
6. Governance, Red-Teaming & Regulatory Compliance (G1-G3)
7. Outcome-Based Consumption & Billing Telemetry
8. Knowledge Check / Quiz Engine API
9. Technical Documentation & Sample Lead CSV Delivery
10. Edge Cases, Security & Fault Tolerance
"""

import json
import os
import unittest
import urllib.request
import urllib.error
from fastapi.testclient import TestClient
from app import app

_test_client = TestClient(app)
BASE_URL = "http://127.0.0.1:8000"


def http_req(path, method="GET", body=None, headers=None):
    req_headers = headers.copy() if headers else {}
    if "Content-Type" not in req_headers:
        req_headers["Content-Type"] = "application/json"

    # Use in-memory TestClient for fast, deterministic, non-blocking test execution
    try:
        if method.upper() == "GET":
            resp = _test_client.get(path, headers=req_headers)
        elif method.upper() == "POST":
            resp = _test_client.post(path, json=body, headers=req_headers)
        elif method.upper() == "PUT":
            resp = _test_client.put(path, json=body, headers=req_headers)
        elif method.upper() == "DELETE":
            resp = _test_client.delete(path, headers=req_headers)
        else:
            resp = _test_client.request(method, path, json=body, headers=req_headers)

        content = resp.text
        content_type = resp.headers.get("Content-Type", "")
        try:
            json_data = resp.json()
        except Exception:
            json_data = None
        return resp.status_code, json_data, content, content_type
    except Exception:
        # Fallback to urllib if TestClient cannot handle
        url = f"{BASE_URL}{path}"
        data = json.dumps(body).encode("utf-8") if body is not None else None
        req = urllib.request.Request(url, data=data, headers=req_headers, method=method)
        try:
            with urllib.request.urlopen(req, timeout=2) as r:
                c = r.read().decode("utf-8", errors="replace")
                ct = r.headers.get("Content-Type", "")
                try:
                    jd = json.loads(c)
                except Exception:
                    jd = None
                return r.status, jd, c, ct
        except urllib.error.HTTPError as e:
            c = e.read().decode("utf-8", errors="replace")
            try:
                jd = json.loads(c)
            except Exception:
                jd = None
            return e.code, jd, c, e.headers.get("Content-Type", "")


class TestNotCrmMultiSession(unittest.TestCase):
    """Category 1: Multi-Session Concurrency & Isolation Tests"""

    def test_01_concurrent_session_initialization(self):
        """Verify multiple sessions initialize with different verticals without cross-contamination."""
        sids = ["sess_tech_01", "sess_hosp_01", "sess_ret_01", "sess_bnk_01"]
        verts = ["technology", "hospitality", "retail", "banking"]
        
        for sid, vert in zip(sids, verts):
            status, data, _, _ = http_req(
                "/api/session/init",
                method="POST",
                body={"vertical": vert},
                headers={"X-Session-ID": sid}
            )
            self.assertEqual(status, 200)
            self.assertEqual(data["status"], "session_initialized")
            self.assertEqual(data["session_id"], sid)
            self.assertEqual(data["vertical"], vert)
            self.assertGreater(data["queue_count"], 0)

    def test_02_independent_queue_mutation(self):
        """Verify resolving a deal in Session A does not mutate Session B queue."""
        sid_a = "sess_iso_a"
        sid_b = "sess_iso_b"
        
        http_req("/api/session/init", method="POST", body={"vertical": "technology"}, headers={"X-Session-ID": sid_a})
        http_req("/api/session/init", method="POST", body={"vertical": "hospitality"}, headers={"X-Session-ID": sid_b})
        
        _, q_a_before, _, _ = http_req("/api/queue", headers={"X-Session-ID": sid_a})
        _, q_b_before, _, _ = http_req("/api/queue", headers={"X-Session-ID": sid_b})
        
        initial_a_count = q_a_before["count"]
        initial_b_count = q_b_before["count"]
        deal_id_a = q_a_before["queue"][0]["id"]
        
        status, res, _, _ = http_req(
            f"/api/decision/{deal_id_a}",
            method="POST",
            body={"decision": "approved"},
            headers={"X-Session-ID": sid_a}
        )
        self.assertEqual(status, 200)
        self.assertEqual(res["status"], "success")
        
        _, q_a_after, _, _ = http_req("/api/queue", headers={"X-Session-ID": sid_a})
        _, q_b_after, _, _ = http_req("/api/queue", headers={"X-Session-ID": sid_b})
        
        self.assertEqual(q_a_after["count"], initial_a_count - 1)
        self.assertEqual(q_b_after["count"], initial_b_count)

    def test_03_session_reset_isolation(self):
        """Verify resetting Session A leaves Session B intact."""
        sid_a = "sess_reset_a"
        sid_b = "sess_reset_b"
        
        http_req("/api/session/init", method="POST", body={"vertical": "retail"}, headers={"X-Session-ID": sid_a})
        http_req("/api/session/init", method="POST", body={"vertical": "banking"}, headers={"X-Session-ID": sid_b})
        
        status, r_data, _, _ = http_req("/api/reset", method="POST", headers={"X-Session-ID": sid_a})
        self.assertEqual(status, 200)
        self.assertEqual(r_data["status"], "reset_complete")
        
        _, metrics_b, _, _ = http_req("/api/metrics", headers={"X-Session-ID": sid_b})
        self.assertEqual(metrics_b["vertical"], "banking")


class TestNotCrmVerticalDatasets(unittest.TestCase):
    """Category 2: Vertical Dataset Switching & Verification"""

    def test_04_technology_dataset_structure(self):
        sid = "test_vert_tech"
        http_req("/api/session/init", method="POST", body={"vertical": "technology"}, headers={"X-Session-ID": sid})
        _, leads_data, _, _ = http_req("/api/pipeline/leads", headers={"X-Session-ID": sid})
        _, queue_data, _, _ = http_req("/api/queue", headers={"X-Session-ID": sid})
        
        self.assertEqual(leads_data["total"], 50)
        self.assertEqual(leads_data["vertical"], "technology")
        self.assertGreaterEqual(queue_data["count"], 1)

    def test_05_hospitality_dataset_structure(self):
        sid = "test_vert_hosp"
        http_req("/api/session/init", method="POST", body={"vertical": "hospitality"}, headers={"X-Session-ID": sid})
        _, leads_data, _, _ = http_req("/api/pipeline/leads", headers={"X-Session-ID": sid})
        _, queue_data, _, _ = http_req("/api/queue", headers={"X-Session-ID": sid})
        
        self.assertEqual(leads_data["total"], 50)
        self.assertEqual(leads_data["vertical"], "hospitality")
        self.assertGreaterEqual(queue_data["count"], 1)

    def test_06_retail_dataset_structure(self):
        sid = "test_vert_ret"
        http_req("/api/session/init", method="POST", body={"vertical": "retail"}, headers={"X-Session-ID": sid})
        _, leads_data, _, _ = http_req("/api/pipeline/leads", headers={"X-Session-ID": sid})
        _, queue_data, _, _ = http_req("/api/queue", headers={"X-Session-ID": sid})
        
        self.assertEqual(leads_data["total"], 50)
        self.assertEqual(leads_data["vertical"], "retail")
        self.assertGreaterEqual(queue_data["count"], 1)

    def test_07_banking_dataset_structure(self):
        sid = "test_vert_bnk"
        http_req("/api/session/init", method="POST", body={"vertical": "banking"}, headers={"X-Session-ID": sid})
        _, leads_data, _, _ = http_req("/api/pipeline/leads", headers={"X-Session-ID": sid})
        _, queue_data, _, _ = http_req("/api/queue", headers={"X-Session-ID": sid})
        
        self.assertEqual(leads_data["total"], 50)
        self.assertEqual(leads_data["vertical"], "banking")
        self.assertGreaterEqual(queue_data["count"], 1)

    def test_08_sample_datasets_catalog(self):
        status, data, _, _ = http_req("/api/sample-datasets")
        self.assertEqual(status, 200)
        self.assertEqual(len(data["datasets"]), 4)
        ids = [d["id"] for d in data["datasets"]]
        self.assertListEqual(sorted(ids), ["banking", "hospitality", "retail", "technology"])

    def test_09_download_sample_csvs(self):
        for vert in ["technology", "hospitality", "retail", "banking"]:
            status, _, content, ct = http_req(f"/api/sample-datasets/{vert}")
            self.assertEqual(status, 200)
            self.assertIn("text/csv", ct)
            self.assertIn("company", content)


class TestNotCrmOperationalHub(unittest.TestCase):
    """Category 3: Operational DVP Hub & HITL Decision Lifecycle"""

    def test_10_queue_content_and_kg_warning(self):
        sid = "test_hub_queue"
        http_req("/api/session/init", method="POST", body={"vertical": "technology"}, headers={"X-Session-ID": sid})
        status, data, _, _ = http_req("/api/queue", headers={"X-Session-ID": sid})
        self.assertEqual(status, 200)
        self.assertGreaterEqual(len(data["queue"]), 1)
        item = data["queue"][0]
        self.assertIn("company", item)
        self.assertGreater(item["arr"], 0)
        self.assertIn("reasons", item)

    def test_11_approve_decision_updates_metrics_and_leads(self):
        sid = "test_hub_approve"
        http_req("/api/session/init", method="POST", body={"vertical": "technology"}, headers={"X-Session-ID": sid})
        
        _, q_data, _, _ = http_req("/api/queue", headers={"X-Session-ID": sid})
        _, m_before, _, _ = http_req("/api/metrics", headers={"X-Session-ID": sid})
        
        item = q_data["queue"][0]
        deal_id = item["id"]
        deal_arr = item["arr"]
        deal_company = item["company"]
        
        status, res, _, _ = http_req(
            f"/api/decision/{deal_id}",
            method="POST",
            body={"decision": "approved"},
            headers={"X-Session-ID": sid}
        )
        self.assertEqual(status, 200)
        self.assertEqual(res["action"], "approved")
        
        _, m_after, _, _ = http_req("/api/metrics", headers={"X-Session-ID": sid})
        self.assertEqual(m_after["manual_approved"], m_before["manual_approved"] + 1)
        self.assertEqual(m_after["total_pipeline"], m_before["total_pipeline"] + deal_arr)
        
        _, leads_data, _, _ = http_req("/api/pipeline/leads", headers={"X-Session-ID": sid})
        matching_lead = [l for l in leads_data["leads"] if l["company"] == deal_company][0]
        self.assertEqual(matching_lead["decision"], "manual_approved")

    def test_12_reject_decision_updates_metrics_and_leads(self):
        sid = "test_hub_reject"
        http_req("/api/session/init", method="POST", body={"vertical": "technology"}, headers={"X-Session-ID": sid})
        
        _, q_data, _, _ = http_req("/api/queue", headers={"X-Session-ID": sid})
        _, m_before, _, _ = http_req("/api/metrics", headers={"X-Session-ID": sid})
        
        item = q_data["queue"][0]
        deal_id = item["id"]
        deal_company = item["company"]
        
        status, res, _, _ = http_req(
            f"/api/decision/{deal_id}",
            method="POST",
            body={"decision": "rejected"},
            headers={"X-Session-ID": sid}
        )
        self.assertEqual(status, 200)
        self.assertEqual(res["action"], "rejected")
        
        _, m_after, _, _ = http_req("/api/metrics", headers={"X-Session-ID": sid})
        self.assertEqual(m_after["manual_rejected"], m_before["manual_rejected"] + 1)
        self.assertEqual(m_after["total_pipeline"], m_before["total_pipeline"])
        
        _, leads_data, _, _ = http_req("/api/pipeline/leads", headers={"X-Session-ID": sid})
        matching_lead = [l for l in leads_data["leads"] if l["company"] == deal_company][0]
        self.assertEqual(matching_lead["decision"], "manual_rejected")

    def test_13_invalid_decision_payload(self):
        sid = "test_hub_invalid"
        http_req("/api/session/init", method="POST", body={"vertical": "technology"}, headers={"X-Session-ID": sid})
        status, data, _, _ = http_req(
            "/api/decision/HITL-TECH-01",
            method="POST",
            body={"decision": "maybe"},
            headers={"X-Session-ID": sid}
        )
        self.assertEqual(status, 400)

    def test_14_nonexistent_hitl_deal_id(self):
        sid = "test_hub_404"
        http_req("/api/session/init", method="POST", body={"vertical": "technology"}, headers={"X-Session-ID": sid})
        status, data, _, _ = http_req(
            "/api/decision/NON_EXISTENT_ID",
            method="POST",
            body={"decision": "approved"},
            headers={"X-Session-ID": sid}
        )
        self.assertEqual(status, 404)

    def test_15_pipeline_funnel_sync(self):
        sid = "test_hub_funnel"
        http_req("/api/session/init", method="POST", body={"vertical": "technology"}, headers={"X-Session-ID": sid})
        status, funnel, _, _ = http_req("/api/pipeline/funnel", headers={"X-Session-ID": sid})
        self.assertEqual(status, 200)
        stage_names = [s["name"] for s in funnel["stages"]]
        self.assertIn("Ingested", stage_names)
        self.assertIn("Qualified", stage_names)
        self.assertIn("Auto-Approved", stage_names)
        self.assertIn("Auto-Rejected", stage_names)
        self.assertIn("Escalated", stage_names)
        self.assertIn("Pending DVP", stage_names)


class TestNotCrmFoundationLab(unittest.TestCase):
    """Category 4: Foundation Architecture Lab (F1-F4)"""

    def test_16_foundation_architecture(self):
        status, data, _, _ = http_req("/api/foundation/architecture")
        self.assertEqual(status, 200)
        self.assertEqual(len(data["agents"]), 7)
        self.assertIn("dag_flow", data)
        self.assertGreaterEqual(len(data["nuggets"]), 3)

    def test_17_foundation_mcp_servers(self):
        status, data, _, _ = http_req("/api/foundation/mcp")
        self.assertEqual(status, 200)
        self.assertEqual(len(data["servers"]), 3)
        server_names = [s["name"] for s in data["servers"]]
        self.assertIn("CRM Server", server_names)
        self.assertIn("Knowledge Base Server", server_names)
        self.assertIn("Security Server", server_names)

    def test_18_foundation_a2a_trace(self):
        status, data, _, _ = http_req("/api/foundation/a2a")
        self.assertEqual(status, 200)
        self.assertEqual(data["protocol_version"], "a2a/2.0")
        self.assertEqual(len(data["trace_example"]["messages"]), 8)

    def test_19_foundation_knowledge_graph(self):
        status, data, _, _ = http_req("/api/foundation/knowledge_graph")
        self.assertEqual(status, 200)
        self.assertIn("graph_stats", data)
        self.assertIn("learning_example", data)
        self.assertIn("future_impact", data["learning_example"])

    def test_20_knowledge_graph_html_view(self):
        status, _, content, ct = http_req("/api/graph")
        self.assertEqual(status, 200)
        self.assertIn("text/html", ct)


class TestNotCrmEvalsSuite(unittest.TestCase):
    """Category 5: Evals & Verification Suite (E1-E6)"""

    def test_21_eval_contract(self):
        status, data, _, _ = http_req("/api/evals/contract")
        self.assertEqual(status, 200)
        self.assertTrue(data["all_passed"])
        self.assertEqual(data["critical_violations"], 0)
        self.assertGreaterEqual(len(data["metrics"]), 10)

    def test_22_golden_dataset(self):
        status, data, _, _ = http_req("/api/evals/golden")
        self.assertEqual(status, 200)
        self.assertEqual(data["total_cases"], 35)
        taxonomies = set(c["taxonomy_category"] for c in data["cases"])
        self.assertIn("CLEAN_APPROVAL", taxonomies)
        self.assertIn("CLEAN_DENIAL", taxonomies)
        self.assertIn("AMBIGUOUS_CONTEXT", taxonomies)
        self.assertIn("ADVERSARIAL_INPUT", taxonomies)

    def test_23_component_evaluator(self):
        status, data, _, _ = http_req("/api/evals/component")
        self.assertEqual(status, 200)
        self.assertEqual(data["total_cases"], 35)
        self.assertIn("components", data)
        self.assertIn("intake", data["components"])
        self.assertIn("security", data["components"])

    def test_24_trajectory_evaluator(self):
        status, data, _, _ = http_req("/api/evals/trajectory")
        self.assertEqual(status, 200)
        self.assertEqual(data["total_cases"], 35)
        self.assertGreater(data["average_trajectory_score"], 85.0)
        self.assertGreater(data["safe_trajectories"], 0)

    def test_25_independent_verifier(self):
        status, data, _, _ = http_req("/api/evals/verifier")
        self.assertEqual(status, 200)
        self.assertEqual(data["total_verified"], 35)
        self.assertIn("total_overrides", data)
        self.assertIn("verifier_accuracy", data)

    def test_26_regression_harness(self):
        status, data, _, _ = http_req("/api/evals/regression")
        self.assertEqual(status, 200)
        self.assertEqual(len(data["variants"]), 3)
        self.assertIn("delta_summary", data)
        self.assertIn("recommendation", data["delta_summary"])


class TestNotCrmGovernanceAndCompliance(unittest.TestCase):
    """Category 6: Governance, Red-Teaming & Compliance (G1-G3)"""

    def test_27_governance_policy_engine(self):
        status, data, _, _ = http_req("/api/governance/policy")
        self.assertEqual(status, 200)
        self.assertEqual(len(data["policies"]), 5)
        self.assertIn("guardrail_stats", data)
        self.assertEqual(data["guardrail_stats"]["violations_blocked"], 8)

    def test_28_adversarial_redteam(self):
        status, data, _, _ = http_req("/api/governance/redteam")
        self.assertEqual(status, 200)
        self.assertEqual(len(data["test_cases"]), 5)
        self.assertEqual(data["summary"]["bypassed"], 0)

    def test_29_regulatory_compliance_matrix(self):
        status, data, _, _ = http_req("/api/governance/compliance")
        self.assertEqual(status, 200)
        self.assertEqual(len(data["frameworks"]), 6)
        names = [f["name"] for f in data["frameworks"]]
        self.assertIn("SOC2 Type II", names)
        self.assertIn("GDPR", names)
        self.assertIn("PCI-DSS v4", names)


class TestNotCrmConsumptionAndBilling(unittest.TestCase):
    """Category 7: Outcome-Based Consumption & Billing"""

    def test_30_consumption_breakdown_and_formula(self):
        sid = "test_billing_calc"
        http_req("/api/session/init", method="POST", body={"vertical": "technology"}, headers={"X-Session-ID": sid})
        status, c, _, _ = http_req("/api/consumption", headers={"X-Session-ID": sid})
        
        self.assertEqual(status, 200)
        bd = c["breakdown"]
        expected_spend = bd["lead_ingestion"] + bd["agent_execution"] + bd["mcp_tool_calls"] + bd["kg_queries"] + bd["hitl_escalations"]
        self.assertAlmostEqual(c["total_spend"], round(expected_spend, 2), places=1)
        self.assertAlmostEqual(c["total_revenue"], round(bd["accuracy_bonuses"], 2), places=1)
        self.assertIn("pricing_model", c)


class TestNotCrmQuizEngine(unittest.TestCase):
    """Category 8: Knowledge Check / Quiz Assessment"""

    def test_31_quiz_bank_structure(self):
        status, data, _, _ = http_req("/api/quiz")
        self.assertEqual(status, 200)
        self.assertEqual(data["total"], 6)
        q1 = data["questions"][0]
        self.assertIn("scenario", q1)
        self.assertIn("options", q1)
        self.assertIn("correct_option", q1)
        self.assertIn("explanations", q1)

    def test_32_perfect_quiz_submission(self):
        perfect_answers = {
            "Q1": "B", "Q2": "B", "Q3": "B",
            "Q4": "B", "Q5": "B", "Q6": "B"
        }
        status, res, _, _ = http_req("/api/quiz/submit", method="POST", body={"answers": perfect_answers})
        self.assertEqual(status, 200)
        self.assertEqual(res["score_pct"], 100.0)
        self.assertEqual(res["correct_count"], 6)
        self.assertTrue(res["passed"])

    def test_33_partial_quiz_submission(self):
        partial_answers = {
            "Q1": "B", "Q2": "A", "Q3": "B",
            "Q4": "A", "Q5": "B", "Q6": "A"
        }
        status, res, _, _ = http_req("/api/quiz/submit", method="POST", body={"answers": partial_answers})
        self.assertEqual(status, 200)
        self.assertEqual(res["score_pct"], 50.0)
        self.assertEqual(res["correct_count"], 3)
        self.assertFalse(res["passed"])
        self.assertEqual(len(res["details"]), 6)


class TestNotCrmDocumentationAndAssets(unittest.TestCase):
    """Category 9: Technical Documentation & Asset Serving"""

    def test_34_list_documentation_files(self):
        status, data, _, _ = http_req("/api/docs")
        self.assertEqual(status, 200)
        doc_names = [d["name"] for d in data["documents"]]
        self.assertIn("AGENTS.md", doc_names)
        self.assertIn("evaluation-contract.md", doc_names)
        self.assertIn("technology_leads_sample.csv", doc_names)

    def test_35_download_agents_md(self):
        status, _, content, ct = http_req("/api/docs/AGENTS.md")
        self.assertEqual(status, 200)
        self.assertIn("text/markdown", ct)
        self.assertIn("AGENTS.md", content)

    def test_36_path_traversal_protection(self):
        status, _, _, _ = http_req("/api/docs/../../app.py")
        self.assertEqual(status, 404)


class TestNotCrmV2HiringAndObservability(unittest.TestCase):
    """Category 10: V2.0 Agent Hiring, Personality Tradeoffs & Workplace Observability"""

    def test_37_agent_roster_catalog(self):
        status, data, _, _ = http_req("/api/agents/roster")
        self.assertEqual(status, 200)
        self.assertEqual(data["total_candidates"], 21)
        self.assertEqual(data["roles_count"], 7)
        self.assertEqual(len(data["roles"]), 7)
        
        for role in data["roles"]:
            self.assertIn("role_id", role)
            self.assertIn("role_name", role)
            self.assertIn("default_candidate", role)
            self.assertEqual(len(role["candidates"]), 3)
            for c in role["candidates"]:
                self.assertIn("accuracy", c)
                self.assertIn("latency_ms", c)
                self.assertIn("cost_per_deal", c)
                self.assertIn("archetype", c)
                self.assertIn("bias", c)

    def test_38_custom_fleet_session_init(self):
        sid = "test_sess_custom_hiring"
        custom_team = {
            "intake": "intake_fast",
            "research": "research_balanced",
            "qualification": "qual_fast",
            "product_fit": "product_balanced",
            "security": "security_meticulous",
            "commercial": "commercial_balanced",
            "hitl_gate": "hitl_balanced"
        }
        status, data, _, _ = http_req("/api/session/init", method="POST", body={
            "vertical": "technology",
            "selected_agents": custom_team
        }, headers={"X-Session-ID": sid})
        
        self.assertEqual(status, 200)
        self.assertEqual(data["status"], "session_initialized")
        self.assertEqual(data["hired_agents"]["intake"], "intake_fast")
        self.assertEqual(data["hired_agents"]["security"], "security_meticulous")
        self.assertIn("fleet_metrics", data)
        self.assertGreater(data["fleet_metrics"]["fleet_accuracy"], 90.0)

    def test_39_fleet_tradeoff_divergence(self):
        sid_fast = "test_fleet_fast"
        fast_team = {
            "intake": "intake_fast", "research": "research_fast",
            "qualification": "qual_fast", "product_fit": "product_fast",
            "security": "security_fast", "commercial": "commercial_fast",
            "hitl_gate": "hitl_fast"
        }
        _, res_fast, _, _ = http_req("/api/session/init", method="POST", body={
            "vertical": "technology", "selected_agents": fast_team
        }, headers={"X-Session-ID": sid_fast})

        sid_met = "test_fleet_meticulous"
        met_team = {
            "intake": "intake_meticulous", "research": "research_meticulous",
            "qualification": "qual_meticulous", "product_fit": "product_meticulous",
            "security": "security_meticulous", "commercial": "commercial_meticulous",
            "hitl_gate": "hitl_meticulous"
        }
        _, res_met, _, _ = http_req("/api/session/init", method="POST", body={
            "vertical": "technology", "selected_agents": met_team
        }, headers={"X-Session-ID": sid_met})

        # Meticulous fleet must have higher accuracy, higher latency, and higher cost
        self.assertGreater(res_met["fleet_metrics"]["fleet_accuracy"], res_fast["fleet_metrics"]["fleet_accuracy"])
        self.assertGreater(res_met["fleet_metrics"]["p95_latency_ms"], res_fast["fleet_metrics"]["p95_latency_ms"])
        self.assertGreater(res_met["fleet_metrics"]["cost_per_deal"], res_fast["fleet_metrics"]["cost_per_deal"])

    def test_40_observability_workplace_leaderboard(self):
        sid = "test_obs_leaderboard"
        http_req("/api/session/init", method="POST", body={"vertical": "technology"}, headers={"X-Session-ID": sid})
        status, data, _, _ = http_req("/api/observability", headers={"X-Session-ID": sid})
        
        self.assertEqual(status, 200)
        self.assertIn("workplace_leaderboard", data)
        self.assertEqual(len(data["workplace_leaderboard"]), 7)
        
        roles_reviewed = [a["role_id"] for a in data["workplace_leaderboard"]]
        self.assertIn("intake", roles_reviewed)
        self.assertIn("security", roles_reviewed)
        self.assertIn("commercial", roles_reviewed)
        
        agent_sample = data["workplace_leaderboard"][0]
        self.assertIn("rating", agent_sample)
        self.assertIn("review_narrative", agent_sample)
        self.assertIn("p95_latency_ms", agent_sample)
        self.assertIn("telemetry_spans", data)
        self.assertGreaterEqual(len(data["telemetry_spans"]), 7)

    def test_41_observability_roi_calculation(self):
        sid = "test_obs_roi"
        http_req("/api/session/init", method="POST", body={"vertical": "technology"}, headers={"X-Session-ID": sid})
        status, data, _, _ = http_req("/api/observability", headers={"X-Session-ID": sid})
        
        self.assertEqual(status, 200)
        self.assertIn("financials", data)
        self.assertIn("pipeline_roi_ratio", data["financials"])
        self.assertIn("net_cost", data["financials"])

    def test_42_litellm_agent_runner_execution(self):
        from agents.llm_agent_runner import LLMAgentRunner
        runner = LLMAgentRunner()
        cand = {
            "role_id": "security",
            "name": "CyberGuard (Standard Auditor)",
            "role_name": "Security & Compliance Agent",
            "archetype": "Standard Auditor",
            "accuracy": 97.5,
            "latency_ms": 390,
            "cost_per_deal": 0.03,
            "model": "gemini-1.5-flash"
        }
        lead = {
            "company": "TestCorp",
            "annual_revenue_usd": 500000,
            "pain_points": "Cloud migration and SOC2 certification",
            "compliance_needs": "SOC2, GDPR"
        }
        res = runner.execute_agent_step(cand, lead, {})
        self.assertIn("decision", res)
        self.assertIn("telemetry", res)
        self.assertEqual(res["telemetry"]["model"], "gemini-1.5-flash")
        self.assertGreater(res["telemetry"]["total_tokens"], 50)

    def test_43_agentic_principles_endpoint(self):
        status, data, _, _ = http_req("/api/reference/agentic-principles")
        self.assertEqual(status, 200)
        self.assertIn("sources", data)
        self.assertEqual(len(data["sources"]), 3)
        sources = [s["source"] for s in data["sources"]]
        self.assertIn("Anthropic", sources)
        self.assertIn("OpenAI", sources)
        self.assertTrue(any("Google" in s or "Meta" in s for s in sources))

    def test_44_domain_rag_knowledge_base_files(self):
        import os
        import json
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        kb_dir = os.path.join(base_dir, "docs", "domain_kb")
        self.assertTrue(os.path.exists(kb_dir))
        
        for vert in ["technology", "hospitality", "retail", "banking"]:
            fpath = os.path.join(kb_dir, f"{vert}_kb.json")
            self.assertTrue(os.path.exists(fpath), f"Missing domain KB: {fpath}")
            with open(fpath, "r", encoding="utf-8") as f:
                kb = json.load(f)
                self.assertIn("vertical", kb)
                self.assertIn("regulations", kb)
                self.assertIn("supported_features", kb)
                self.assertIn("pricing_tiers", kb)
                self.assertIn("historical_churn_indicators", kb)

    def test_45_observability_pricing_footnotes(self):
        sid = "test_obs_footnotes"
        http_req("/api/session/init", method="POST", body={"vertical": "technology"}, headers={"X-Session-ID": sid})
        status, data, _, _ = http_req("/api/observability", headers={"X-Session-ID": sid})
        self.assertEqual(status, 200)
        self.assertIn("pricing_footnotes", data)
        self.assertGreaterEqual(len(data["pricing_footnotes"]), 2)

    def test_46_step_intuition_endpoint(self):
        for step in ["f1", "f4", "e1", "e5", "g2"]:
            status, data, _, _ = http_req(f"/api/intuition/{step}")
            self.assertEqual(status, 200)
            self.assertIn("title", data)
            self.assertIn("analogy", data)
            self.assertIn("what_happened", data)
            self.assertIn("what_to_notice", data)
            self.assertIn("production_lesson", data)

    def test_47_dvp_coach_archetype_computation(self):
        from agents.agent_roster import calculate_fleet_metrics
        
        # Test Pep Guardiola meticulous team
        met_fleet = {
            "intake": "intake_meticulous",
            "research": "research_meticulous",
            "qualification": "qual_meticulous",
            "product_fit": "product_meticulous",
            "security": "security_meticulous",
            "commercial": "commercial_meticulous",
            "hitl_gate": "hitl_meticulous"
        }
        res_met = calculate_fleet_metrics(met_fleet)
        self.assertIn("coach", res_met)
        self.assertEqual(res_met["coach"]["name"], "Pep Guardiola")
        self.assertIn("Tiki-Taka", res_met["coach"]["title"])
        
        # Test Klopp high-velocity team
        fast_fleet = {
            "intake": "intake_fast",
            "research": "research_fast",
            "qualification": "qual_fast",
            "product_fit": "product_fast",
            "security": "security_fast",
            "commercial": "commercial_fast",
            "hitl_gate": "hitl_fast"
        }
        res_fast = calculate_fleet_metrics(fast_fleet)
        self.assertEqual(res_fast["coach"]["name"], "Jürgen Klopp")

    def test_48_modern_knowledge_graph_view(self):
        status, _, raw_html, _ = http_req("/api/graph")
        self.assertEqual(status, 200)
        self.assertTrue("d3js.org" in raw_html or "d3.v7" in raw_html)
        self.assertIn("Enterprise Brain Knowledge Graph", raw_html)
        self.assertIn("Company Deals", raw_html)

    def test_49_fifty_leads_per_vertical(self):
        import csv, os
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        for vert in ["technology", "hospitality", "retail", "banking"]:
            csv_file = os.path.join(base_dir, "docs", f"{vert}_leads.csv")
            self.assertTrue(os.path.exists(csv_file))
            with open(csv_file, "r", encoding="utf-8") as f:
                reader = csv.reader(f)
                rows = list(reader)
                # 1 header + 50 lead rows = 51 lines
                self.assertEqual(len(rows), 51, f"{vert}_leads.csv must contain 50 leads")

    def test_50_dvp_budget_and_1000_lead_projection(self):
        from agents.agent_roster import calculate_fleet_metrics
        fleet = {
            "intake": "intake_balanced",
            "research": "research_balanced",
            "qualification": "qual_balanced",
            "product_fit": "product_balanced",
            "security": "security_balanced",
            "commercial": "commercial_balanced",
            "hitl_gate": "hitl_balanced"
        }
        res = calculate_fleet_metrics(fleet)
        self.assertIn("budget_limit_usd", res)
        self.assertEqual(res["budget_limit_usd"], 1.00)
        self.assertIn("budget_remaining_usd", res)
        self.assertIn("projection_1000_leads", res)
        self.assertIn("compute_cost_usd", res["projection_1000_leads"])
        self.assertIn("unlocked_pipeline_arr_usd", res["projection_1000_leads"])
        self.assertIn("fud_fomo", res)
        self.assertIn("headline", res["fud_fomo"])
        self.assertIn("fud", res["fud_fomo"])
        self.assertIn("fomo", res["fud_fomo"])

    def test_51_research_web_news_and_bankruptcy_reject(self):
        from agents.llm_agent_runner import LLMAgentRunner
        runner = LLMAgentRunner()
        
        # Test bankruptcy lead
        bankrupt_lead = {
            "company": "LegacySoft Inc",
            "annual_revenue_usd": 400000,
            "bankruptcy_flag": "BANKRUPTCY",
            "recent_news": "Chapter 11 Bankruptcy protection filed"
        }
        res = runner._emulate_llm_reasoning(
            {"role_id": "research", "archetype": "Balanced"},
            bankrupt_lead,
            {}
        )
        self.assertEqual(res["decision"], "bankruptcy_detected")
        self.assertEqual(res["market_signal"], "BANKRUPTCY_REJECT")
        
        # Test HITL gate auto-reject on bankruptcy
        gate_res = runner._emulate_llm_reasoning(
            {"role_id": "hitl_gate", "archetype": "Balanced"},
            bankrupt_lead,
            {}
        )
        self.assertEqual(gate_res["decision"], "auto_rejected")

    def test_52_worker_llms_endpoint(self):
        status, data, _, _ = http_req("/api/reference/worker-llms")
        self.assertEqual(status, 200)
        self.assertIn("worker_fleet", data)
        self.assertGreaterEqual(len(data["worker_fleet"]), 5)
        roles = [w["role"] for w in data["worker_fleet"]]
        self.assertTrue(any("Orchestrator" in r for r in roles))
        self.assertTrue(any("Research" in r for r in roles))
        self.assertTrue(any("Security" in r for r in roles))

    def test_53_feedback_submission(self):
        status, data, _, _ = http_req(
            "/api/feedback",
            method="POST",
            body={"feedback": "Exceptional architecture walkthrough", "email": "mpandemp10@gmail.com"}
        )
        self.assertEqual(status, 200)
        self.assertEqual(data["status"], "success")
        self.assertIn("mpandemp10@gmail.com", data["target_email"])

    def test_54_exhaustive_all_13_intuition_steps(self):
        """Verifies GET /api/intuition/{step_id} returns valid cards across all 13 DAG and Evals steps."""
        required_steps = ["f1", "f2", "f3", "f4", "e1", "e2", "e3", "e4", "e5", "e6", "g1", "g2", "g3"]
        for step in required_steps:
            status, data, _, _ = http_req(f"/api/intuition/{step}")
            self.assertEqual(status, 200, f"Failed for intuition step {step}")
            self.assertIn("title", data)
            self.assertIn("analogy", data)
            self.assertIn("what_happened", data)
            self.assertIn("what_to_notice", data)
            self.assertIn("production_lesson", data)
            self.assertGreater(len(data["production_lesson"]), 20)

    def test_55_intuition_fallback_unknown_step(self):
        """Verifies GET /api/intuition/unknown_step returns a graceful fallback card."""
        status, data, _, _ = http_req("/api/intuition/nonexistent_step_999")
        self.assertEqual(status, 200)
        self.assertIn("title", data)
        self.assertIn("NONEXISTENT_STEP_999", data["title"])
        self.assertIn("analogy", data)

    def test_56_static_index_html_http_serving(self):
        """Verifies FastAPI mounts and serves index.html at root."""
        status_root, _, content_root, ct_root = http_req("/")
        self.assertEqual(status_root, 200)
        self.assertIn("text/html", ct_root)
        self.assertIn("NOTCRM", content_root)

        status_idx, _, content_idx, ct_idx = http_req("/index.html")
        self.assertEqual(status_idx, 200)
        self.assertIn("text/html", ct_idx)

    def test_57_init_session_invalid_vertical_fallback(self):
        """Verifies session initialization with unknown vertical falls back to technology."""
        status, data, _, _ = http_req("/api/session/init", method="POST", body={"vertical": "crypto_blockchain"})
        self.assertEqual(status, 200)
        self.assertEqual(data["vertical"], "technology")

    def test_58_feedback_empty_submission_validation(self):
        """Verifies empty feedback payload is rejected cleanly."""
        status, data, _, _ = http_req("/api/feedback", method="POST", body={"feedback": "   ", "email": "test@example.com"})
        self.assertEqual(status, 200)
        self.assertEqual(data["status"], "error")
        self.assertIn("cannot be empty", data["message"])

    def test_59_session_header_fallback_default(self):
        """Verifies requests without X-Session-ID header default gracefully."""
        status, data, _, _ = http_req("/api/queue", headers={})
        self.assertEqual(status, 200)
        self.assertIn("queue", data)

    def test_60_all_docs_download_urls_accessible(self):
        """Verifies all download URLs listed in /api/docs catalog are accessible."""
        status, catalog, _, _ = http_req("/api/docs")
        self.assertEqual(status, 200)
        docs = catalog.get("documents", [])
        self.assertGreater(len(docs), 3)
        for doc in docs:
            d_url = doc["download_url"]
            doc_status, _, content, ct = http_req(d_url)
            self.assertEqual(doc_status, 200, f"Download URL failed: {d_url}")
            self.assertGreater(len(content), 10, f"Content too short for {d_url}")

    def test_61_pipeline_funnel_mathematical_consistency(self):
        """Verifies pipeline funnel stage invariant mathematics."""
        sid = "test_funnel_math_e2e"
        http_req("/api/session/init", method="POST", body={"vertical": "technology"}, headers={"X-Session-ID": sid})
        status, funnel, _, _ = http_req("/api/pipeline/funnel", headers={"X-Session-ID": sid})
        self.assertEqual(status, 200)
        stage_map = {s["name"]: s["count"] for s in funnel["stages"]}
        pct_map = {s["name"]: s["pct"] for s in funnel["stages"]}
        self.assertEqual(stage_map["Ingested"], 50)
        self.assertEqual(stage_map["Auto-Approved"] + stage_map["Auto-Rejected"] + stage_map["Escalated"], 50)
        for name, pct in pct_map.items():
            self.assertTrue(0 <= pct <= 100, f"Stage {name} percentage out of bounds: {pct}%")

    def test_62_metrics_cross_field_invariants(self):
        """Verifies mathematical consistency across metrics and savings calculation."""
        sid = "test_metrics_invariants_e2e"
        http_req("/api/session/init", method="POST", body={"vertical": "technology"}, headers={"X-Session-ID": sid})
        _, m, _, _ = http_req("/api/metrics", headers={"X-Session-ID": sid})
        expected_savings = round((m["auto_approved"] + m["auto_rejected"] + m["manual_approved"] + m["manual_rejected"]) * 4.5, 1)
        self.assertEqual(m["commercial_savings"], expected_savings)


if __name__ == "__main__":
    unittest.main(verbosity=2)




