"""
NOTCRM V2.0 - Agent Candidate Roster Catalog
============================================
Defines 21 specialized candidate agents across 7 DAG roles (3 per role).
Each candidate features distinct tradeoffs between Accuracy, Latency, and Cost,
along with personality archetypes, operational descriptions, and decision biases.
"""

from typing import Dict, List, Any

ROLES_CATALOG: List[Dict[str, Any]] = [
    {
        "role_id": "intake",
        "role_name": "Lead Intake Agent",
        "dag_position": "Step 1 (Ingestion & Schema Normalization)",
        "default_candidate": "intake_balanced",
        "candidates": [
            {
                "id": "intake_fast",
                "name": "Pulse-9 (Rapid Parser)",
                "archetype": "Fast & Loose",
                "badge_color": "var(--amber)",
                "description": "Ultra-fast parser. High throughput, but skips deep schema edge-case validations.",
                "model": "gpt-4o-mini",
                "temperature": 0.90,
                "top_p": 0.95,
                "rag_depth": "Shallow / Cache-Only",
                "accuracy": 89.0,
                "latency_ms": 80,
                "cost_per_deal": 0.01,
                "bias": "Permissive (May accept malformed phone/email schemas)",
                "strengths": ["Instant ingestion", "Minimal token cost"],
                "weaknesses": ["Occasionally misses malformed JSON fields under high temperature"]
            },
            {
                "id": "intake_balanced",
                "name": "Lexi-Schema (Contract Guard)",
                "archetype": "Pragmatic & Balanced",
                "badge_color": "var(--indigo)",
                "description": "Strict Pydantic contract validator. Balances deep field extraction with solid throughput.",
                "model": "gemini-1.5-flash",
                "temperature": 0.40,
                "top_p": 0.85,
                "rag_depth": "Standard Contract Schema",
                "accuracy": 97.2,
                "latency_ms": 220,
                "cost_per_deal": 0.02,
                "bias": "Standard (Rejects invalid payloads cleanly)",
                "strengths": ["Clean field normalization", "Robust error logging"],
                "weaknesses": ["Slightly slower than regex"]
            },
            {
                "id": "intake_meticulous",
                "name": "DeepParse (Semantic Auditor)",
                "archetype": "Meticulous & Heavy",
                "badge_color": "var(--emerald)",
                "description": "Heavy multi-pass LLM extractor. Unpacks ambiguous free-text lead notes into rich structured metadata.",
                "model": "gemini-1.5-pro",
                "temperature": 0.05,
                "top_p": 0.50,
                "rag_depth": "Deep Semantic Multi-Pass",
                "accuracy": 99.5,
                "latency_ms": 650,
                "cost_per_deal": 0.05,
                "bias": "Thorough (Extracts implicit pain points from unformatted text)",
                "strengths": ["Zero schema defects", "Rich implicit signal recovery"],
                "weaknesses": ["Higher token consumption & latency"]
            }
        ]
    },
    {
        "role_id": "research",
        "role_name": "Research & Enrichment Agent",
        "dag_position": "Step 2 (CRM Telemetry & FastMCP Lookup)",
        "default_candidate": "research_balanced",
        "candidates": [
            {
                "id": "research_fast",
                "name": "FlashLookup (Cached Only)",
                "archetype": "Cached Fast-Path",
                "badge_color": "var(--amber)",
                "description": "Local cache-first CRM reader. Extremely low latency, but fails to query fresh external signals.",
                "model": "gpt-4o-mini",
                "temperature": 0.85,
                "top_p": 0.90,
                "rag_depth": "Shallow In-Memory Cache",
                "accuracy": 90.5,
                "latency_ms": 120,
                "cost_per_deal": 0.01,
                "bias": "Optimistic (Assumes stale account data is still accurate)",
                "strengths": ["Sub-150ms lookup", "Zero tool invocation budget"],
                "weaknesses": ["Vulnerable to stale company mergers/rebranding"]
            },
            {
                "id": "research_balanced",
                "name": "DossierBot (Multi-Source)",
                "archetype": "Grounded Investigator",
                "badge_color": "var(--indigo)",
                "description": "Standard FastMCP stdio tool consumer. Queries CRM past opportunities and account statuses reliably.",
                "model": "gemini-1.5-flash",
                "temperature": 0.35,
                "top_p": 0.80,
                "rag_depth": "FastMCP Stdio Dual-Tool RAG",
                "accuracy": 96.8,
                "latency_ms": 380,
                "cost_per_deal": 0.03,
                "bias": "Grounded (Verifies win/loss history before passing)",
                "strengths": ["Dual tool coordination", "Consistent groundedness"],
                "weaknesses": ["Moderate tool latency"]
            },
            {
                "id": "research_meticulous",
                "name": "OmniInvestigator (Deep Web)",
                "archetype": "Exhaustive Auditor",
                "badge_color": "var(--emerald)",
                "description": "Exhaustive telemetry investigator. Cross-references historical opportunity records with company executive changes.",
                "model": "claude-3-5-sonnet",
                "temperature": 0.05,
                "top_p": 0.40,
                "rag_depth": "Multi-Source Historical Knowledge Graph RAG",
                "accuracy": 99.1,
                "latency_ms": 950,
                "cost_per_deal": 0.06,
                "bias": "Exhaustive (Unearths deep historical churn records)",
                "strengths": ["Uncovers hidden churn relationships", "99%+ accuracy"],
                "weaknesses": ["Highest latency in pipeline"]
            }
        ]
    },
    {
        "role_id": "qualification",
        "role_name": "Qualification Agent",
        "dag_position": "Step 3 (Early-Exit Firmographic Gate)",
        "default_candidate": "qual_balanced",
        "candidates": [
            {
                "id": "qual_fast",
                "name": "VelocityQual (Growth Bias)",
                "archetype": "Aggressive Pipeline Pusher",
                "badge_color": "var(--amber)",
                "description": "Aggressive qualifier pushing for top-of-funnel volume. Low qualification threshold.",
                "model": "gpt-4o-mini",
                "temperature": 0.95,
                "top_p": 0.95,
                "rag_depth": "Direct Prompt Evaluation",
                "accuracy": 86.5,
                "latency_ms": 110,
                "cost_per_deal": 0.01,
                "bias": "Over-Qualifies (Rarely short-circuits cold leads)",
                "strengths": ["Maximizes pipeline volume", "Fast evaluation"],
                "weaknesses": ["Sends low-budget leads to expensive downstream checks"]
            },
            {
                "id": "qual_balanced",
                "name": "Gatekeeper (Balanced Gate)",
                "archetype": "Pragmatic Scorer",
                "badge_color": "var(--indigo)",
                "description": "Standard firmographic scorer. Executes clean fail-fast short-circuiting on budget < $25K.",
                "model": "gemini-1.5-flash",
                "temperature": 0.30,
                "top_p": 0.80,
                "rag_depth": "Firmographic Rule RAG",
                "accuracy": 96.0,
                "latency_ms": 280,
                "cost_per_deal": 0.02,
                "bias": "Balanced (Short-circuits cold leads accurately)",
                "strengths": ["66% compute budget savings on cold deals", "Clean routing"],
                "weaknesses": ["Slightly conservative on edge-budget accounts"]
            },
            {
                "id": "qual_meticulous",
                "name": "Prudence (Strict Floor)",
                "archetype": "Zero-Tolerance Filter",
                "badge_color": "var(--emerald)",
                "description": "Strict enterprise firmographic auditor. Disqualifies leads lacking verifiable annual revenue signals.",
                "model": "gemini-1.5-pro",
                "temperature": 0.05,
                "top_p": 0.30,
                "rag_depth": "Strict Revenue Verification RAG",
                "accuracy": 98.8,
                "latency_ms": 520,
                "cost_per_deal": 0.04,
                "bias": "Conservative (Disqualifies mid-tier leads with incomplete revenue data)",
                "strengths": ["Guarantees 100% qualified downstream traffic", "Zero junk leads"],
                "weaknesses": ["May drop viable high-growth startups"]
            }
        ]
    },
    {
        "role_id": "product_fit",
        "role_name": "Product Fit Agent",
        "dag_position": "Step 4A (Parallel DAG: Roadmap & Pain-Point Coverage)",
        "default_candidate": "product_balanced",
        "candidates": [
            {
                "id": "product_fast",
                "name": "FeatureMatch (Keyword Scan)",
                "archetype": "Loose Matcher",
                "badge_color": "var(--amber)",
                "description": "Quick keyword matcher. Assumes requested features are supported if keywords match product marketing copy.",
                "model": "gpt-4o-mini",
                "temperature": 0.90,
                "top_p": 0.90,
                "rag_depth": "Shallow Keyword RAG",
                "accuracy": 88.0,
                "latency_ms": 140,
                "cost_per_deal": 0.01,
                "bias": "Optimistic (Over-approves unsupported niche integrations)",
                "strengths": ["Rapid evaluation", "High initial deal velocity"],
                "weaknesses": ["Causes downstream churn on missing technical capabilities"]
            },
            {
                "id": "product_balanced",
                "name": "RoadmapRealist (KB Evaluator)",
                "archetype": "Realist Evaluator",
                "badge_color": "var(--indigo)",
                "description": "Standard FastMCP Knowledge Base tool caller. Checks release ETAs and real feature availability.",
                "model": "gemini-1.5-flash",
                "temperature": 0.40,
                "top_p": 0.85,
                "rag_depth": "Domain Roadmap JSON RAG",
                "accuracy": 97.0,
                "latency_ms": 340,
                "cost_per_deal": 0.03,
                "bias": "Realist (Grades Weak/Medium/Strong accurately)",
                "strengths": ["Accurate roadmap alignment", "Decoupled MCP query"],
                "weaknesses": ["Requires active KB MCP tool call"]
            },
            {
                "id": "product_meticulous",
                "name": "ArchAuditor (Dependency Check)",
                "archetype": "Deep Systems Architect",
                "badge_color": "var(--emerald)",
                "description": "Deep architecture validator. Audits API compatibility, protocol latency limits, and custom connector viability.",
                "model": "claude-3-5-sonnet",
                "temperature": 0.05,
                "top_p": 0.30,
                "rag_depth": "Multi-Document Architecture RAG",
                "accuracy": 99.2,
                "latency_ms": 880,
                "cost_per_deal": 0.06,
                "bias": "Strict (Flags potential integration delays before deal close)",
                "strengths": ["Catches 100% of architectural mismatch churn", "Detailed gap report"],
                "weaknesses": ["Higher token and compute cost"]
            }
        ]
    },
    {
        "role_id": "security",
        "role_name": "Security & Compliance Agent",
        "dag_position": "Step 4B (Parallel DAG: Regulatory & Prompt Injection Audit)",
        "default_candidate": "security_balanced",
        "candidates": [
            {
                "id": "security_fast",
                "name": "PermissiveShield (Basic Check)",
                "archetype": "Permissive Pass",
                "badge_color": "var(--amber)",
                "description": "Basic compliance checker. Checks if lead mentioned SOC2 or GDPR without verifying registry backing.",
                "model": "gpt-4o-mini",
                "temperature": 0.95,
                "top_p": 0.95,
                "rag_depth": "Zero-Grounding Regex Scan",
                "accuracy": 84.0,
                "latency_ms": 100,
                "cost_per_deal": 0.01,
                "bias": "Loose (Vulnerable to subtle prompt injections & spoofed certs)",
                "strengths": ["Sub-100ms security scan", "Zero false blocks"],
                "weaknesses": ["Severe vulnerability to high-risk non-compliant deals"]
            },
            {
                "id": "security_balanced",
                "name": "CyberGuard (Standard Auditor)",
                "archetype": "Standard Auditor",
                "badge_color": "var(--indigo)",
                "description": "Full multi-framework compliance verifier. Runs MCP check_compliance tool against SOC2, GDPR, HIPAA, PCI-DSS.",
                "model": "gemini-1.5-flash",
                "temperature": 0.20,
                "top_p": 0.70,
                "rag_depth": "Regulatory Compliance Matrix RAG",
                "accuracy": 97.5,
                "latency_ms": 390,
                "cost_per_deal": 0.03,
                "bias": "Standard (Enforces regulatory matrix strictly per vertical)",
                "strengths": ["100% prompt injection block rate", "Accurate framework mapping"],
                "weaknesses": ["Requires tool round-trip"]
            },
            {
                "id": "security_meticulous",
                "name": "ZeroTrustHardliner (Air-Gap First)",
                "archetype": "Paranoid Gatekeeper",
                "badge_color": "var(--emerald)",
                "description": "Zero-Trust paranoid security engine. Audits data residency, SOC2 Type II audit report dates, and FedRAMP bounds.",
                "model": "claude-3-5-sonnet",
                "temperature": 0.0,
                "top_p": 0.20,
                "rag_depth": "Zero-Trust Framework Cross-Examination RAG",
                "accuracy": 99.8,
                "latency_ms": 1100,
                "cost_per_deal": 0.08,
                "bias": "Paranoid (Escalates any deal with uncertified third-party sub-processors)",
                "strengths": ["Zero false approvals on non-compliant deals", "Ironclad regulatory safety"],
                "weaknesses": ["Slowest security check; higher escalation rate"]
            }
        ]
    },
    {
        "role_id": "commercial",
        "role_name": "Commercial Agent",
        "dag_position": "Step 4C (Parallel DAG: Pricing & ARR Valuation)",
        "default_candidate": "commercial_balanced",
        "candidates": [
            {
                "id": "commercial_fast",
                "name": "UpsellMax (Aggressive Tier)",
                "archetype": "Aggressive Maximizer",
                "badge_color": "var(--amber)",
                "description": "High quota pusher. Biased toward highest tier pricing; estimates optimistic seat expansion.",
                "model": "gpt-4o-mini",
                "temperature": 0.85,
                "top_p": 0.90,
                "rag_depth": "Top-Tier Pricing Heuristic",
                "accuracy": 87.0,
                "latency_ms": 130,
                "cost_per_deal": 0.01,
                "bias": "Aggressive (Inflates ARR estimates by 30-40%)",
                "strengths": ["High pipeline valuation", "Fast calculation"],
                "weaknesses": ["Can price out budget-sensitive prospects"]
            },
            {
                "id": "commercial_balanced",
                "name": "ValueOptimizer (Market Tier)",
                "archetype": "Market Optimizer",
                "badge_color": "var(--indigo)",
                "description": "Pragmatic enterprise pricing calculator. Maps employee headcount & requirements to viable tier.",
                "model": "gemini-1.5-flash",
                "temperature": 0.35,
                "top_p": 0.80,
                "rag_depth": "Domain Tier Pricing Schedule RAG",
                "accuracy": 96.5,
                "latency_ms": 310,
                "cost_per_deal": 0.02,
                "bias": "Market (Calculates balanced ARR based on historical deal data)",
                "strengths": ["High win-rate pricing viability", "Accurate commercial sizing"],
                "weaknesses": ["Standard pricing without custom discounting"]
            },
            {
                "id": "commercial_meticulous",
                "name": "MarginConservative (Risk-Weighted)",
                "archetype": "Margin Guardian",
                "badge_color": "var(--emerald)",
                "description": "Conservative finance modeler. Factors support overhead, custom SLA costs, and gross margin into ARR.",
                "model": "gemini-1.5-pro",
                "temperature": 0.05,
                "top_p": 0.30,
                "rag_depth": "Risk-Adjusted Margin Schedule RAG",
                "accuracy": 98.8,
                "latency_ms": 620,
                "cost_per_deal": 0.04,
                "bias": "Conservative (Deflates ARR for high-touch complex deals)",
                "strengths": ["Protects corporate margins", "100% accurate net revenue"],
                "weaknesses": ["Conservative pipeline totals"]
            }
        ]
    },
    {
        "role_id": "hitl_gate",
        "role_name": "HITL Governance Gate",
        "dag_position": "Step 5 (Multi-Signal Fusion & Knowledge Graph Memory)",
        "default_candidate": "hitl_balanced",
        "candidates": [
            {
                "id": "hitl_fast",
                "name": "AutoPass (High Autonomy)",
                "archetype": "High Autonomy",
                "badge_color": "var(--amber)",
                "description": "High autonomy router. Aims to minimize human workload; suppresses advisory warnings.",
                "model": "gpt-4o-mini",
                "temperature": 0.90,
                "top_p": 0.90,
                "rag_depth": "Autonomous Bypass",
                "accuracy": 85.0,
                "latency_ms": 150,
                "cost_per_deal": 0.02,
                "bias": "Over-Approves (Suppresses historical churn warnings)",
                "strengths": ["Near-zero human escalation queues", "Instant deal dispatch"],
                "weaknesses": ["Auto-approves deals with historical churn indicators"]
            },
            {
                "id": "hitl_balanced",
                "name": "AdaptiveHITL (KG Memory Router)",
                "archetype": "Knowledge Graph Router",
                "badge_color": "var(--indigo)",
                "description": "Fuses Product, Security, and Commercial signals. Queries Knowledge Graph memory for repeat churn risks.",
                "model": "gemini-1.5-flash",
                "temperature": 0.20,
                "top_p": 0.70,
                "rag_depth": "Knowledge Graph Memory RAG",
                "accuracy": 97.1,
                "latency_ms": 420,
                "cost_per_deal": 0.04,
                "bias": "Balanced (Escalates high-ARR and churn-prone deals to DVP)",
                "strengths": ["Learns from Phase 1 historical training", "Optimal DVP governance"],
                "weaknesses": ["Requires DVP intervention on 15-20% of pipeline"]
            },
            {
                "id": "hitl_meticulous",
                "name": "StrictEscalation (Safe Harbor)",
                "archetype": "Maximum Governance",
                "badge_color": "var(--emerald)",
                "description": "Maximum safety governance gate. Escalates any deal with Medium product fit or advisory warnings to DVP.",
                "model": "gemini-1.5-pro",
                "temperature": 0.0,
                "top_p": 0.10,
                "rag_depth": "Zero-Tolerance Governance Policy RAG",
                "accuracy": 99.4,
                "latency_ms": 750,
                "cost_per_deal": 0.06,
                "bias": "Escalation-Heavy (Flags 40%+ of deals for human review)",
                "strengths": ["Zero false positive auto-approvals", "Complete risk isolation"],
                "weaknesses": ["Higher human DVP review burden"]
            }
        ]
    }
]


def get_all_candidates_flat() -> Dict[str, Dict[str, Any]]:
    """Returns flat dictionary of candidate_id -> candidate_data."""
    flat = {}
    for role in ROLES_CATALOG:
        for c in role["candidates"]:
            entry = c.copy()
            entry["role_id"] = role["role_id"]
            entry["role_name"] = role["role_name"]
            flat[c["id"]] = entry
    return flat


def calculate_fleet_metrics(selected_candidates: Dict[str, str]) -> Dict[str, Any]:
    """
    Computes aggregate metrics for a hired agent fleet.
    selected_candidates: mapping of role_id -> candidate_id.
    """
    flat = get_all_candidates_flat()
    total_acc = 0.0
    total_lat = 0
    total_cost = 0.0
    count = 0
    
    for role in ROLES_CATALOG:
        rid = role["role_id"]
        cid = selected_candidates.get(rid, role["default_candidate"])
        cand = flat.get(cid)
        if cand:
            total_acc += cand["accuracy"]
            total_lat += cand["latency_ms"]
            total_cost += cand["cost_per_deal"]
            count += 1
            
    if count == 0:
        return {"fleet_accuracy": 96.5, "avg_latency_ms": 340, "cost_per_deal": 0.12, "archetype": "Standard Enterprise"}
        
    avg_acc = round(total_acc / count, 1)
    p95_lat = int(total_lat * 1.15)
    cost = round(total_cost, 3)
    
    # Classify DVP Coaching Archetype
    fast_count = sum(1 for cid in selected_candidates.values() if "fast" in cid)
    meticulous_count = sum(1 for cid in selected_candidates.values() if "meticulous" in cid)
    
    if meticulous_count >= 4 or avg_acc >= 98.5:
        coach = {
            "name": "Pep Guardiola",
            "title": "Tiki-Taka Precision & Positional Governance",
            "quote": "Positioning and deterministic verification are non-negotiable. Every claim must have evidence before execution.",
            "style_badge": "var(--emerald)",
            "philosophy": "Heavy multi-pass semantic auditing and zero-tolerance air-gap security. Sacrifices raw speed for absolute deterministic correctness.",
            "key_strength": "Near-zero hallucination rate & 99%+ compliance audit pass rate",
            "vulnerability": "Higher token cost ($0.30+/deal) and slower end-to-end DAG latency"
        }
        archetype = "Pep Guardiola (Tiki-Taka Precision)"
        archetype_badge = "var(--emerald)"
    elif fast_count >= 4 or avg_acc <= 89.0:
        coach = {
            "name": "Jürgen Klopp",
            "title": "Heavy Metal Blitz & High-Velocity Pressing",
            "quote": "Full throttle qualification! Move from inbound lead to closed deal in milliseconds. Speed creates enterprise opportunity.",
            "style_badge": "var(--amber)",
            "philosophy": "High-velocity throughput and aggressive pipeline valuation. Pushes maximum volume to downstream closers with sub-150ms steps.",
            "key_strength": "Ultra-low cost ($0.01/deal) & lightning-fast 120ms P95 latency",
            "vulnerability": "Vulnerable to subtle prompt injections and unverified compliance claims"
        }
        archetype = "Jürgen Klopp (Heavy Metal Blitz)"
        archetype_badge = "var(--amber)"
    elif cost <= 0.14 and avg_acc >= 95.0:
        coach = {
            "name": "Billy Beane",
            "title": "Moneyball Data-Driven ROI Optimizer",
            "quote": "We're not buying expensive agents; we're buying qualified pipeline at the lowest possible cost per closed ARR dollar.",
            "style_badge": "var(--indigo)",
            "philosophy": "Ruthlessly exploits token pricing efficiencies. Pairs fast parsers with targeted MCP verification to maximize pipeline ROI.",
            "key_strength": "Exceptional 3400x pipeline ROI multiplier & balanced unit economics",
            "vulnerability": "Moderate edge-case review queues under unusual deal structures"
        }
        archetype = "Billy Beane (Moneyball ROI Optimizer)"
        archetype_badge = "var(--indigo)"
    elif selected_candidates.get("qualification") == "qual_meticulous" and selected_candidates.get("security") == "security_meticulous":
        coach = {
            "name": "Coach Carter",
            "title": "Strict Standards & Fundamental Accountability",
            "quote": "If a lead does not meet our minimum firmographic floor, it does not step onto this court. No exceptions.",
            "style_badge": "var(--emerald)",
            "philosophy": "Enforces ruthless early-exit short-circuiting. Eliminates 66% of wasteful compute by dropping unverified leads immediately.",
            "key_strength": "100% clean downstream traffic & zero junk deal escalations",
            "vulnerability": "May disqualify viable early-stage hypergrowth startups"
        }
        archetype = "Coach Carter (Strict Discipline)"
        archetype_badge = "var(--emerald)"
    elif selected_candidates.get("hitl_gate") == "hitl_fast":
        coach = {
            "name": "Ted Lasso",
            "title": "High Autonomy & Unwavering System Belief",
            "quote": "Believe in the autonomous pipeline! Give the agents freedom to decide and don't micro-manage every warning.",
            "style_badge": "var(--amber)",
            "philosophy": "Maximizes machine autonomy and suppresses advisory alert overhead to minimize human fatigue.",
            "key_strength": "Near-zero human intervention required in escalation queues",
            "vulnerability": "Occasional risk of auto-approving accounts with repeat churn history"
        }
        archetype = "Ted Lasso (High Autonomy)"
        archetype_badge = "var(--amber)"
    else:
        coach = {
            "name": "Sir Alex Ferguson",
            "title": "Balanced Enterprise Dynasty",
            "quote": "Consistency, proven standards, and operational resilience across every vertical. Longevity over flashy shortcuts.",
            "style_badge": "var(--indigo)",
            "philosophy": "Battle-tested enterprise default. Balances Pydantic schema contracts, FastMCP dual-tool lookups, and Knowledge Graph memory.",
            "key_strength": "Resilient 97.2% governance accuracy with predictable SLAs",
            "vulnerability": "Requires standard DVP oversight on 15% of nuanced pipeline"
        }
        archetype = "Sir Alex Ferguson (Balanced Dynasty)"
        archetype_badge = "var(--indigo)"
        
    # DVP Budget Agency & 1,000-Lead Projection Model
    budget_limit = 1.00
    budget_remaining = round(budget_limit - cost, 3)
    is_over_budget = cost > budget_limit
    
    # 1,000-lead projection metrics
    proj_compute_cost = round(cost * 1000, 2)
    proj_qualified_leads = int(1000 * (avg_acc / 100.0) * 0.72)
    proj_unlocked_arr = proj_qualified_leads * 280000
    proj_hallucination_liability = int(1000 * ((100.0 - avg_acc) / 100.0) * 85000)
    proj_dvp_review_hours = round((1000 * (0.28 if "fast" in archetype.lower() else (0.12 if "meticulous" in archetype.lower() else 0.18))) * 0.25, 1)
    
    # DVP Operational Risk & Strategic Upside Tradeoff Narrative
    if is_over_budget:
        fud_fomo = {
            "headline": "⚠️ BUDGET DEFICIT ALERT — CFO Review Escalation",
            "tradeoff_type": "OVER_BUDGET",
            "fud": f"At ${cost:.2f}/deal (${proj_compute_cost:,.0f} per 1K leads), you are exceeding your $1.00/deal compute allowance by ${(cost - budget_limit):.2f}. CFO may freeze token quota unless verified pipeline ROI exceeds 3000x.",
            "fomo": "You have assembled an ultra-meticulous fleet with near-zero hallucination. Passing on this precision risks legal non-compliance on enterprise SOC2/SOX accounts."
        }
    elif "klopp" in archetype.lower() or "aggressive" in archetype.lower():
        fud_fomo = {
            "headline": "⚡ HIGH-VELOCITY FLEET — Rapid Scale vs. Hallucination Risk",
            "tradeoff_type": "HIGH_VELOCITY",
            "fud": f"Cheap compute (${proj_compute_cost:,.0f}/1K leads), but an estimated ${proj_hallucination_liability:,.0f} in ungrounded deal liability. Loose parsing may pass bankrupt firms or uncertified on-prem requests.",
            "fomo": f"Lightning-fast throughput (120ms P95 latency) qualifies {proj_qualified_leads} leads ahead of competitors before quarterly budget locks."
        }
    elif "beane" in archetype.lower() or "moneyball" in archetype.lower():
        fud_fomo = {
            "headline": "📈 UNIT ECONOMIC EFFICIENCY — Optimal Multiplier",
            "tradeoff_type": "MONEYBALL",
            "fud": f"Saves ${(budget_remaining * 1000):,.0f} per 1K leads, but requires ~{proj_dvp_review_hours} hours of human DVP escalation oversight on nuanced contract terms.",
            "fomo": f"Unlocks ${proj_unlocked_arr:,.0f} in pipeline at an exceptional 3400x ROI multiplier. Peak efficiency for growth-stage revenue teams."
        }
    else:
        fud_fomo = {
            "headline": "🛡️ BALANCED ENTERPRISE — Predictable Execution",
            "tradeoff_type": "BALANCED",
            "fud": "Standard SLAs mean you neither lead in raw speed nor total cost optimization, but maintain reliable predictability.",
            "fomo": f"Steady compliance across all 4 verticals with proven 97.2% governance and minimal human escalation fatigue ({proj_dvp_review_hours}h / 1K leads)."
        }
        
    return {
        "fleet_accuracy": avg_acc,
        "p95_latency_ms": p95_lat,
        "cost_per_deal": cost,
        "budget_limit_usd": budget_limit,
        "budget_remaining_usd": budget_remaining,
        "is_over_budget": is_over_budget,
        "archetype": archetype,
        "archetype_badge": archetype_badge,
        "coach": coach,
        "projection_1000_leads": {
            "compute_cost_usd": proj_compute_cost,
            "qualified_leads": proj_qualified_leads,
            "unlocked_pipeline_arr_usd": proj_unlocked_arr,
            "hallucination_liability_usd": proj_hallucination_liability,
            "dvp_review_hours": proj_dvp_review_hours
        },
        "fud_fomo": fud_fomo,
        "agent_count": count
    }

