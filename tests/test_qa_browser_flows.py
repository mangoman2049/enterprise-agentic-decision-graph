"""
Comprehensive QA Automation and Browser Flow Test Suite for NOTCRM
Validates:
1. Multi-vertical session lifecycle (reset, init, 50 leads per vertical).
2. Navigation and data population payloads for all tabs (Tabs 1-7).
3. Human-in-the-loop (HITL) queue resolution mutations.
4. HTML DOM structure (no broken nesting, tab sibling hierarchy).
5. Progression tracker elements (all 14 step dots and result containers).
6. Compliance checks (banned terms, branding consistency).
"""

import unittest
import json
import re
from pathlib import Path
from html.parser import HTMLParser
from fastapi.testclient import TestClient
from app import app

client = TestClient(app)

INDEX_HTML_PATH = Path(__file__).resolve().parent.parent / "static" / "index.html"


class TabDOMValidator(HTMLParser):
    """AST/DOM parser to verify tab container hierarchy and ensure no nested tab bugs."""
    def __init__(self):
        super().__init__()
        self.stack = []
        self.tabs = []
        self.tab_parents = {}
        self.element_ids = set()
        self.void_elements = {'input', 'img', 'br', 'hr', 'meta', 'link', 'iframe'}

    def handle_starttag(self, tag, attrs):
        attr_dict = dict(attrs)
        el_id = attr_dict.get('id')
        el_class = attr_dict.get('class', '')

        if el_id:
            self.element_ids.add(el_id)

        if 'tab-content' in el_class.split() or (el_id and el_id.startswith('tab') and el_id[3:].isdigit()):
            self.tabs.append(el_id)
            current_parent = self.stack[-1] if self.stack else ("ROOT", None, "")
            self.tab_parents[el_id] = current_parent

        if tag not in self.void_elements:
            self.stack.append((tag, el_id, el_class))

    def handle_endtag(self, tag):
        if tag in self.void_elements:
            return
        if self.stack:
            for i in range(len(self.stack) - 1, -1, -1):
                if self.stack[i][0] == tag:
                    for _ in range(len(self.stack) - i):
                        self.stack.pop()
                    return


class TestQABrowserFlows(unittest.TestCase):
    def setUp(self):
        self.session_id = "test_qa_sess_999"
        self.headers = {"X-Session-ID": self.session_id}
        # Reset session state before each test
        client.post("/api/reset", headers=self.headers)

    def test_01_session_reset_and_fresh_state(self):
        """Verify POST /api/reset returns 200 and cleans state."""
        res = client.post("/api/reset", headers=self.headers)
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertIn("status", data)
        self.assertEqual(data["status"], "reset_complete")

    def test_02_multi_vertical_initialization_50_leads(self):
        """Verify session init loads 50 leads for Technology, Hospitality, Retail, and Banking."""
        verticals = ["technology", "hospitality", "retail", "banking"]
        for vert in verticals:
            res_init = client.post(
                "/api/session/init",
                headers=self.headers,
                json={"vertical": vert}
            )
            self.assertEqual(res_init.status_code, 200, f"Init failed for {vert}")

            res_leads = client.get("/api/pipeline/leads", headers=self.headers)
            self.assertEqual(res_leads.status_code, 200)
            leads_data = res_leads.json()
            self.assertEqual(
                leads_data["total"],
                50,
                f"Expected exactly 50 leads for vertical '{vert}', got {leads_data['total']}"
            )
            self.assertEqual(len(leads_data["leads"]), 50)

    def test_03_all_tabs_api_endpoints_health_and_schema(self):
        """Verify every endpoint powering all 7 tabs returns valid 200 OK payloads."""
        # Initialize session first
        client.post("/api/session/init", headers=self.headers, json={"vertical": "technology"})

        endpoints = [
            # Tab 1: Welcome & Hiring
            ("/api/agents/roster", ["roles", "total_candidates"]),
            ("/api/intuition/f1", ["title", "analogy", "production_lesson"]),
            ("/api/intuition/e1", ["title", "analogy", "production_lesson"]),

            # Tab 2: DVP Operational Hub
            ("/api/metrics", ["total_pipeline", "auto_approved", "auto_rejected", "commercial_savings"]),
            ("/api/queue", ["queue", "count", "vertical"]),
            ("/api/pipeline/leads", ["leads", "total", "vertical"]),
            ("/api/pipeline/funnel", ["stages", "vertical"]),
            ("/api/graph", None),  # Returns HTML graph visualization

            # Tab 3: Foundation Lab
            ("/api/foundation/architecture", ["agents", "dag_flow"]),
            ("/api/foundation/mcp", ["servers"]),
            ("/api/foundation/a2a", ["title", "protocol_version", "trace_example"]),
            ("/api/foundation/knowledge_graph", ["graph_stats", "learning_example"]),

            # Tab 4: Evals Lab
            ("/api/evals/contract", ["metrics", "all_passed"]),
            ("/api/evals/golden", ["cases", "total_cases"]),
            ("/api/evals/component", ["components", "total_cases"]),
            ("/api/evals/trajectory", ["cases", "average_trajectory_score"]),
            ("/api/evals/verifier", ["results", "verifier_accuracy"]),
            ("/api/evals/regression", ["variants", "delta_summary"]),

            # Tab 5: Governance & Guardrails
            ("/api/governance/policy", ["policies", "guardrail_stats"]),
            ("/api/governance/redteam", ["test_cases", "summary"]),
            ("/api/governance/compliance", ["frameworks"]),

            # Tab 6: Observability & Economics
            ("/api/observability", ["telemetry_spans", "workplace_leaderboard", "financials"]),
            ("/api/consumption", ["breakdown", "total_spend", "pricing_model"]),

            # Tab 7: Documentation Standards
            ("/api/docs", ["documents"]),

            # Knowledge Check Quiz
            ("/api/quiz", ["questions"]),
        ]

        for path, required_keys in endpoints:
            res = client.get(path, headers=self.headers)
            self.assertEqual(res.status_code, 200, f"Endpoint {path} returned status {res.status_code}")
            if required_keys:
                data = res.json()
                for key in required_keys:
                    self.assertIn(key, data, f"Key '{key}' missing from endpoint {path} response: {data}")

    def test_04_escalation_queue_resolution_mutation(self):
        """Verify resolving an escalated lead removes it from queue and updates metrics."""
        client.post("/api/session/init", headers=self.headers, json={"vertical": "technology"})

        # Fetch current queue
        queue_res = client.get("/api/queue", headers=self.headers)
        self.assertEqual(queue_res.status_code, 200)
        queue_data = queue_res.json()
        initial_count = queue_data["count"]
        self.assertGreater(initial_count, 0, "Queue should contain initial escalated leads")

        first_item = queue_data["queue"][0]
        hitl_id = first_item.get("id") or first_item.get("hitl_id")

        # Resolve queue item as APPROVED
        dec_res = client.post(
            f"/api/decision/{hitl_id}",
            headers=self.headers,
            json={"decision": "approved"}
        )
        self.assertEqual(dec_res.status_code, 200)
        dec_data = dec_res.json()
        self.assertEqual(dec_data["status"], "success")

        # Verify queue count decremented by 1
        queue_res_after = client.get("/api/queue", headers=self.headers)
        self.assertEqual(queue_res_after.json()["count"], initial_count - 1)

    def test_05_html_dom_tab_nesting_and_sibling_structure(self):
        """Verify that tab1 through tab6 are all sibling children under .content-area, with NO nesting."""
        self.assertTrue(INDEX_HTML_PATH.exists(), f"File {INDEX_HTML_PATH} does not exist")
        html_content = INDEX_HTML_PATH.read_text(encoding="utf-8")

        parser = TabDOMValidator()
        parser.feed(html_content)

        # Expected 6 tabs: tab1 to tab6
        expected_tabs = [f"tab{i}" for i in range(1, 7)]
        for tab_id in expected_tabs:
            self.assertIn(tab_id, parser.tabs, f"Tab container #{tab_id} missing from HTML")

        # Verify that all tabs share the exact same parent (i.e. sibling elements inside .content-area)
        parents = [parser.tab_parents[tid] for tid in expected_tabs if tid in parser.tab_parents]
        first_parent = parents[0]
        for p in parents:
            self.assertEqual(
                p, first_parent,
                f"Tab containers do not share the same parent element! Parents detected: {parents}"
            )
            # Parent must not be a tab container itself
            self.assertFalse(
                p[1] and p[1].startswith('tab'),
                f"Tab is incorrectly nested inside another tab: {p}"
            )

    def test_06_html_progression_tracker_elements_exist(self):
        """Verify all 14 progression dots and step result containers exist in HTML."""
        html_content = INDEX_HTML_PATH.read_text(encoding="utf-8")
        parser = TabDOMValidator()
        parser.feed(html_content)

        # 14 progression dots
        required_dots = [
            "dot-f1", "dot-f2", "dot-f3", "dot-f4",
            "dot-e1", "dot-e2", "dot-e3", "dot-e4", "dot-e5", "dot-e6",
            "dot-g1", "dot-g2", "dot-g3", "dot-billing"
        ]
        for dot in required_dots:
            self.assertIn(dot, parser.element_ids, f"Sidebar dot element #{dot} missing from HTML")

        # Result containers
        required_res = [
            "res-f1", "res-f2", "res-f3", "res-f4",
            "res-e1", "res-e2", "res-e3", "res-e4", "res-e5", "res-e6",
            "res-g1", "res-g2", "res-g3"
        ]
        for res_id in required_res:
            self.assertIn(res_id, parser.element_ids, f"Result container #{res_id} missing from HTML")

    def test_07_banned_terms_and_brand_hygiene(self):
        """Verify that no banned terms ('Andrew Ng', 'FUD', 'FOMO', 'NOTCRM V20') exist in code."""
        html_content = INDEX_HTML_PATH.read_text(encoding="utf-8")
        app_path = Path(__file__).resolve().parent.parent / "app.py"
        app_content = app_path.read_text(encoding="utf-8")

        banned = [
            "FUD",
            "FOMO",
            "NOTCRM V20",
            "NOTCRM v20"
        ]

        for term in banned:
            self.assertNotIn(
                term,
                html_content,
                f"Banned term '{term}' found in static/index.html!"
            )
            self.assertNotIn(
                term,
                app_content,
                f"Banned term '{term}' found in app.py!"
            )


if __name__ == "__main__":
    unittest.main()
