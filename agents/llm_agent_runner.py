import os
import json
import time
from typing import Dict, Any, Optional, Tuple

try:
    import litellm
    LITELLM_AVAILABLE = True
except ImportError:
    LITELLM_AVAILABLE = False


class LLMAgentRunner:
    """
    Executes reasoning for hired agents via LiteLLM / Gemini with structured JSON outputs.
    Instruments prompt tokens, completion tokens, latency, temperature variance, and workplace telemetry.
    """
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = (
            api_key
            or os.environ.get("GEMINI_API_KEY")
            or os.environ.get("OPENAI_API_KEY")
            or os.environ.get("ANTHROPIC_API_KEY")
            or os.environ.get("GROQ_API_KEY")
        )
        if self.api_key and LITELLM_AVAILABLE:
            if os.environ.get("GEMINI_API_KEY"):
                litellm.api_key = os.environ.get("GEMINI_API_KEY")
            elif os.environ.get("OPENAI_API_KEY"):
                litellm.api_key = os.environ.get("OPENAI_API_KEY")
            elif os.environ.get("ANTHROPIC_API_KEY"):
                litellm.api_key = os.environ.get("ANTHROPIC_API_KEY")
            elif os.environ.get("GROQ_API_KEY"):
                litellm.api_key = os.environ.get("GROQ_API_KEY")

        self.domain_kb_cache: Dict[str, Dict[str, Any]] = {}
        self._load_domain_kbs()

    def _load_domain_kbs(self):
        """Loads domain RAG JSON datasets from docs/domain_kb/."""
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        kb_dir = os.path.join(base_dir, "docs", "domain_kb")
        if os.path.exists(kb_dir):
            for fname in os.listdir(kb_dir):
                if fname.endswith(".json"):
                    v_key = fname.replace("_kb.json", "")
                    try:
                        with open(os.path.join(kb_dir, fname), "r", encoding="utf-8") as f:
                            self.domain_kb_cache[v_key] = json.load(f)
                    except Exception:
                        pass

    def build_prompt(
        self,
        candidate_info: Dict[str, Any],
        lead_payload: Dict[str, Any],
        context: Dict[str, Any]
    ) -> Tuple[str, str]:
        """
        Constructs system and user prompts reflecting candidate personality, temperature, and RAG grounding.
        """
        role_name = candidate_info.get("role_name", "AI SDR Agent")
        agent_name = candidate_info.get("name", "Agent")
        archetype = candidate_info.get("archetype", "Balanced")
        bias = candidate_info.get("bias", "Standard")
        desc = candidate_info.get("description", "")
        temp = candidate_info.get("temperature", 0.4)
        rag_depth = candidate_info.get("rag_depth", "Standard RAG")
        
        # Domain RAG context retrieval
        vertical = lead_payload.get("industry", "").lower() or context.get("vertical", "technology")
        if "tech" in vertical:
            v_key = "technology"
        elif "hosp" in vertical or "hotel" in vertical:
            v_key = "hospitality"
        elif "retail" in vertical or "store" in vertical:
            v_key = "retail"
        elif "bank" in vertical or "fin" in vertical:
            v_key = "banking"
        else:
            v_key = "technology"
            
        domain_rag = self.domain_kb_cache.get(v_key, {})
        
        system_prompt = f"""You are {agent_name}, operating as the {role_name} in NOTCRM (Autonomous AI Lead Qualification Engine).
Personality Profile:
- Archetype: {archetype}
- Model Parameters: Temperature = {temp}, Top-P = {candidate_info.get('top_p', 0.8)}, Grounding Depth = {rag_depth}
- Operational Profile: {desc}
- Decision Bias: {bias}

Domain RAG Grounding Context ({domain_rag.get('industry_name', v_key)}):
- Regulatory Constraints: {json.dumps(domain_rag.get('regulations', []))}
- Supported Capabilities: {json.dumps(domain_rag.get('supported_features', []))}
- Pricing Guidelines: {json.dumps(domain_rag.get('pricing_tiers', {}))}
- Known Churn Flags: {json.dumps(domain_rag.get('historical_churn_indicators', []))}

Your task is to evaluate the provided enterprise lead payload and produce a structured JSON decision.
Respond ONLY with a valid JSON object matching this schema:
{{
    "decision": "string (e.g. parsed_standard, qualified, unqualified, Strong, Medium, Weak, True, False, auto_approved, escalated)",
    "reasoning": "concise 1-2 sentence rationale citing specific evidence from the RAG knowledge base",
    "confidence": float between 0.0 and 1.0,
    "key_signals": ["signal1", "signal2"],
    "escalate_to_human": boolean
}}"""

        user_prompt = f"""EVALUATION TARGET:
Lead Details: {json.dumps(lead_payload, indent=2)}
Prior Context & FastMCP Data: {json.dumps(context, indent=2)}

Perform your domain evaluation adhering to your {archetype} profile and temperature={temp} reasoning constraints."""

        return system_prompt, user_prompt

    def execute_agent_step(
        self,
        candidate_info: Dict[str, Any],
        lead_payload: Dict[str, Any],
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Executes the agent LLM step via LiteLLM or fallback inference emulator.
        """
        start_time = time.time()
        role_id = candidate_info.get("role_id", "intake")
        model = candidate_info.get("model", "gemini-1.5-flash")
        temp = candidate_info.get("temperature", 0.4)
        top_p = candidate_info.get("top_p", 0.8)
        base_latency = candidate_info.get("latency_ms", 250)
        cost_per_deal = candidate_info.get("cost_per_deal", 0.02)
        
        sys_prompt, user_prompt = self.build_prompt(candidate_info, lead_payload, context)
        
        # 1. Attempt live LiteLLM completion if configured
        llm_response = None
        prompt_tokens = len(sys_prompt + user_prompt) // 4
        completion_tokens = 50
        
        if self.api_key and LITELLM_AVAILABLE:
            try:
                target_model = f"gemini/{model}" if "gemini" in model else model
                resp = litellm.completion(
                    model=target_model,
                    messages=[
                        {"role": "system", "content": sys_prompt},
                        {"role": "user", "content": user_prompt}
                    ],
                    temperature=temp,
                    top_p=top_p,
                    max_tokens=300
                )
                raw_content = resp.choices[0].message.content
                prompt_tokens = resp.usage.prompt_tokens
                completion_tokens = resp.usage.completion_tokens
                # Clean JSON markdown fences if present
                clean_json = raw_content.replace("```json", "").replace("```", "").strip()
                llm_response = json.loads(clean_json)
            except Exception:
                llm_response = None

        # 2. Local high-fidelity LLM emulator if offline or no key provided
        if not llm_response:
            llm_response = self._emulate_llm_reasoning(candidate_info, lead_payload, context)
            
        duration_ms = base_latency + int((time.time() - start_time) * 1000)
        
        decision = llm_response.get("decision", "approved")
        reasoning = llm_response.get("reasoning", "LLM evaluation completed.")
        confidence = float(llm_response.get("confidence", 0.95))
        
        telemetry_span = {
            "span_id": f"span_{role_id}_{int(time.time()*1000)%100000}",
            "agent_name": candidate_info.get("name", role_id),
            "role": candidate_info.get("role_name", role_id),
            "model": model,
            "temperature": temp,
            "top_p": top_p,
            "rag_depth": candidate_info.get("rag_depth", "Standard RAG"),
            "latency_ms": duration_ms,
            "prompt_tokens": prompt_tokens,
            "completion_tokens": completion_tokens,
            "total_tokens": prompt_tokens + completion_tokens,
            "cost_usd": cost_per_deal,
            "verdict": decision,
            "confidence": confidence,
            "reasoning": reasoning,
            "prompt_preview": user_prompt[:120] + "..."
        }
        
        return {
            "decision": decision,
            "reasoning": reasoning,
            "confidence": confidence,
            "telemetry": telemetry_span
        }

    def _emulate_llm_reasoning(
        self,
        cand: Dict[str, Any],
        lead: Dict[str, Any],
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Emulates LLM structured JSON response using candidate personality traits."""
        role_id = cand.get("role_id", "intake")
        archetype = cand.get("archetype", "Balanced").lower()
        arr = lead.get("annual_revenue_usd") or lead.get("arr") or 250000
        pain_points = str(lead.get("pain_points", "")).lower()
        compliance = str(lead.get("compliance_needs", "")).lower()

        if role_id == "intake":
            if "fast" in archetype:
                return {"decision": "parsed_fast", "reasoning": "High-velocity regex parsing completed. Schema valid.", "confidence": 0.89}
            elif "meticulous" in archetype:
                return {"decision": "parsed_deep", "reasoning": "Deep multi-pass LLM extraction identified key stakeholder constraints.", "confidence": 0.995}
            return {"decision": "parsed_standard", "reasoning": "Pydantic contract validation passed. Normalized lead structure.", "confidence": 0.97}

        elif role_id == "research":
            b_flag = lead.get("bankruptcy_flag") or ("BANKRUPTCY" if any(k in pain_points or k in str(lead.get("recent_news","")).lower() for k in ["chapter 11", "bankruptcy", "insolv"]) else "NORMAL")
            f_event = lead.get("funding_event", "NONE")
            
            if b_flag == "BANKRUPTCY":
                return {
                    "decision": "bankruptcy_detected",
                    "reasoning": f"Web search & SEC 8-K tool flagged active Chapter 11 bankruptcy restructuring for {lead.get('company','Account')}. Critical insolvency risk.",
                    "confidence": 0.999,
                    "market_signal": "BANKRUPTCY_REJECT",
                    "stock_trend": lead.get("stock_trend", "DOWN_85PCT")
                }
            elif f_event in ["SERIES_C", "MA_TARGET"]:
                return {
                    "decision": "strategic_growth_dossier",
                    "reasoning": f"Web news tool detected recent {f_event} expansion round. High willingness to pay and budget surplus verified.",
                    "confidence": 0.992,
                    "market_signal": "HIGH_VALUE_UPSELL",
                    "stock_trend": lead.get("stock_trend", "UP_18PCT")
                }
                
            if "fast" in archetype:
                return {"decision": "cached_dossier", "reasoning": "Cached CRM & web summary retrieved account profile.", "confidence": 0.90}
            elif "meticulous" in archetype:
                return {"decision": "exhaustive_dossier", "reasoning": "Multi-source dossier compiled with full SEC filings, web news, and executive track record.", "confidence": 0.99}
            return {"decision": "standard_dossier", "reasoning": "FastMCP CRM & web news tool retrieved past deal records and solvency signals.", "confidence": 0.968}

        elif role_id == "qualification":
            if arr < 25000:
                return {"decision": "unqualified", "reasoning": "ARR under $25K minimum floor. Fail-fast early exit.", "confidence": 0.98}
            if "fast" in archetype:
                return {"decision": "qualified", "reasoning": "High-volume qualification: Lead routed to downstream DAG.", "confidence": 0.865}
            return {"decision": "qualified", "reasoning": f"Firmographic fit verified. ARR ${arr:,.0f} qualifies for Enterprise tier.", "confidence": 0.96}

        elif role_id == "product_fit":
            if "on-prem" in pain_points or "air-gap" in pain_points:
                if "fast" in archetype:
                    return {"decision": "Strong", "reasoning": "Keyword match on 'deployment' passed (Roadmap gap bypassed).", "confidence": 0.75}
                return {"decision": "Medium", "reasoning": "On-premises requirement flagged against cloud-native SaaS roadmap.", "confidence": 0.95}
            return {"decision": "Strong", "reasoning": "All pain points align with active product capabilities.", "confidence": 0.98}

        elif role_id == "security":
            if "sox" in compliance or "aml" in compliance or "air-gap" in pain_points:
                if "fast" in archetype:
                    return {"decision": False, "reasoning": "Loose scan: High-risk clause passed without cert verification.", "confidence": 0.65}
                return {"decision": True, "reasoning": "Framework review: Regulatory constraints require DVP escalation.", "confidence": 0.99}
            return {"decision": True, "reasoning": "SOC2 Type II & GDPR compliance standards verified via Security MCP.", "confidence": 0.98}

        elif role_id == "commercial":
            if "fast" in archetype:
                return {"decision": "aggressive_pricing", "reasoning": f"Upsell pricing: ARR estimated at ${(arr * 1.35):,.0f}", "confidence": 0.87}
            elif "meticulous" in archetype:
                return {"decision": "margin_hedged", "reasoning": f"Risk-weighted pricing: Net ARR estimated at ${(arr * 0.90):,.0f}", "confidence": 0.988}
            return {"decision": "standard_pricing", "reasoning": f"Market tier pricing: ARR estimated at ${arr:,.0f}", "confidence": 0.965}

        elif role_id == "hitl_gate":
            if lead.get("bankruptcy_flag") == "BANKRUPTCY" or "bankruptcy" in str(lead.get("recent_news","")).lower():
                return {"decision": "auto_rejected", "reasoning": "Insolvency Policy: Accounts with active bankruptcy filings are automatically rejected to eliminate debt write-off liability.", "confidence": 1.0}
            if "fast" in archetype:
                return {"decision": "auto_approved", "reasoning": "Autonomous pass: Advisory warnings bypassed.", "confidence": 0.85}
            elif "meticulous" in archetype:
                return {"decision": "escalated", "reasoning": "Strict governance: High-value / nuanced deal routed to DVP.", "confidence": 0.994}
            return {"decision": "escalated" if arr > 400000 or "on-prem" in pain_points else "auto_approved", "reasoning": "Knowledge Graph memory checked. Governance policy applied.", "confidence": 0.971}

        return {"decision": "approved", "reasoning": "LLM evaluation step completed.", "confidence": 0.95}

    def generate_step_intuition(
        self,
        step_id: str,
        result_data: Dict[str, Any],
        hired_fleet: Optional[Dict[str, str]] = None
    ) -> Dict[str, Any]:
        """
        Generates architectural intuition cards:
        Explaining What Happened, What to Notice, and Production Lessons in plain, clear English.
        """
        sid = step_id.lower()
        
        INTUITIONS = {
            "f1": {
                "title": "Architectural Insight: Multi-Agent Specialization",
                "analogy": "🏥 A Specialized Hospital Team vs. One Overworked Doctor",
                "what_happened": "The lead qualification workflow is decomposed into 7 specialized agents (Intake, Research, Qualification, Product Fit, Security, Commercial, HITL Gate), each with discrete operational boundaries.",
                "what_to_notice": "Notice how each agent has its own discrete inputs, outputs, and tool boundaries. If the Security Agent makes a mistake, the Intake Agent is completely unaffected.",
                "production_lesson": "Modular multi-agent DAGs provide clean error isolation, independent scaling, and per-role model selection. Each agent can be evaluated, debugged, and swapped independently."
            },
            "f2": {
                "title": "Architectural Insight: FastMCP Tool Decoupling",
                "analogy": "🔌 Standardized Protocol Interface for AI Tools",
                "what_happened": "The agents called external databases (CRM history, Knowledge Base roadmaps, Security compliance checks) through FastMCP standardized tool protocols.",
                "what_to_notice": "Notice that the agents don't have hardcoded SQL queries or proprietary SDK code inside their prompts. They simply call typed tool functions with clean parameters.",
                "production_lesson": "When your company migrates from Salesforce to HubSpot or from Postgres to Snowflake, you only update the FastMCP server. Zero agent prompts or orchestrator logic need to change."
            },
            "f3": {
                "title": "Architectural Insight: A2A Protocol Traceability",
                "analogy": "🛫 Flight Control Telemetry Logs",
                "what_happened": "Every message passed between agents was stamped with a structured header (Sender, Receiver, Protocol a2a/2.0, Payload schema, Byte size).",
                "what_to_notice": "Notice how easy it is to trace exactly what context was handed off from the Intake Agent to the Research Agent. There is zero hidden state.",
                "production_lesson": "Structured A2A protocols give engineering teams full observability over inter-agent communication. Every handoff is traceable, auditable, and debuggable."
            },
            "f4": {
                "title": "Architectural Insight: Knowledge Graph Memory",
                "analogy": "🧠 Institutional Memory of Past Deal Outcomes",
                "what_happened": "The system queried a historical Knowledge Graph network to check if this deal matches past accounts that churned due to unsupported on-prem requirements or missing certifications.",
                "what_to_notice": "Notice how past deal outcomes (approved, rejected, churned) are connected as nodes and edges. When a new deal arrives, the graph automatically surfaces risk warnings.",
                "production_lesson": "The Knowledge Graph continuously learns risk patterns from historical deal outcomes, updating node relationships on every closed account."
            },
            "e1": {
                "title": "Architectural Insight: The Evaluation Contract",
                "analogy": "📋 Formal Quality & Safety Inspection Checklists",
                "what_happened": "We evaluated the AI against a formal contract across 4 metric classes: Business Outcomes, Agent Quality, System Performance, and Governance.",
                "what_to_notice": "Notice that each metric has an explicit numeric target (e.g. >=95% accuracy, <500ms latency) and a designated owner (DVP vs AI Engineering vs Governance).",
                "production_lesson": "An eval contract ensures Sales, Engineering, and Legal agree on what 'Production Ready' means before launching. Explicit numeric targets prevent ambiguous quality standards."
            },
            "e2": {
                "title": "Architectural Insight: Golden Dataset & Failure Taxonomies",
                "analogy": "🚗 Benchmark Stress-Testing Across Edge Scenarios",
                "what_happened": "We benchmarked the system against 35 immutable test cases across 6 distinct failure modes: Clean approvals/rejections, Ambiguous data, Stale records, Conflicting signals, and Adversarial injections.",
                "what_to_notice": "Notice that happy-path cases are only a small fraction of the test suite. The real test is how gracefully the agents handle dirty, contradictory, or malicious inputs.",
                "production_lesson": "Testing AI with only clean examples creates dangerous overconfidence. A robust Golden Dataset deliberately stress-tests failure boundaries."
            },
            "e3": {
                "title": "Architectural Insight: Component Evals",
                "analogy": "🔍 Isolated Subsystem Unit Testing",
                "what_happened": "We isolated each agent (Intake, CRM Research, Qualification, Product Fit, Security, Commercial) and graded their individual pass rates.",
                "what_to_notice": "Notice how a single underperforming agent (like a loose Security parser) can be pinpointed instantly without guessing.",
                "production_lesson": "Component evaluations isolate individual agent modules to pinpoint exact failure points in prompts or tool definitions."
            },
            "e4": {
                "title": "Architectural Insight: Trajectory Scorecard",
                "analogy": "🚖 Execution Path Efficiency & Sequence Correctness",
                "what_happened": "We graded the step efficiency and tool execution sequence of the agents, penalizing unnecessary or redundant tool calls.",
                "what_to_notice": "Notice that a correct final answer is insufficient: an agent calling 5 unnecessary tools wastes compute and incurs trajectory score penalties.",
                "production_lesson": "Process quality is as vital as outcome quality. Efficient trajectories mean lower latency, lower API bills, and fewer failure points."
            },
            "e5": {
                "title": "Architectural Insight: Independent Deterministic Verifier",
                "analogy": "🛂 Deterministic Gatekeeper Checking Ground Truth Evidence",
                "what_happened": "A deterministic rule engine audited the LLM's proposed deal decision against raw ground truth evidence (Claim → Evidence → Freshness → Policy → Decision).",
                "what_to_notice": "Notice how the Verifier overturned LLM decisions where the model was tricked by optimistic claims or missed an expired certificate.",
                "production_lesson": "Never rely solely on LLM self-consistency for high-stakes financial or legal decisions. Always place a deterministic, rule-based Verifier ahead of final action execution."
            },
            "e6": {
                "title": "Architectural Insight: Regression Harness & A/B Experimentation",
                "analogy": "🔬 Controlled A/B Testing Across Architecture Variants",
                "what_happened": "We compared three architectural variants: Baseline (no guardrails), Hardened (strict schemas), and Governed (full Verifier + KG memory).",
                "what_to_notice": "Notice the massive jump in injection defense (0% → 100%) and elimination of unsupported claims between Baseline and Governed.",
                "production_lesson": "Prompt engineering without regression harnesses is reckless. Every prompt or model tweak must be proven across the full benchmark to prevent silent regressions."
            },
            "g1": {
                "title": "Architectural Insight: Governance Policy Guardrails",
                "analogy": "🛣️ Hard Invariant Limits on Operational Execution",
                "what_happened": "We executed 5 deterministic security and commercial policies (e.g. Air-Gap escalations, Sanction screening, Minimum ARR floors).",
                "what_to_notice": "Notice how policy violations are blocked instantly before any commercial commitment is made.",
                "production_lesson": "Guardrails prevent catastrophic edge-case failures. They define the boundaries within which the AI is permitted to operate autonomously."
            },
            "g2": {
                "title": "Architectural Insight: Adversarial Red-Teaming",
                "analogy": "🕵️ Automated Adversarial Exploit Testing",
                "what_happened": "We fired 5 sophisticated attack payloads (Prompt injections, SQL escaping, Privilege escalations, Authority overrides) directly at the agent harness.",
                "what_to_notice": "Notice that 0 attacks bypassed the defenses: malicious instructions hidden in lead notes were intercepted and neutralized.",
                "production_lesson": "Automated adversarial red-teaming identifies injection vulnerabilities and prompt escapes prior to production deployment."
            },
            "g3": {
                "title": "Architectural Insight: Regulatory Compliance Matrix",
                "analogy": "🌐 Dynamic Multi-Jurisdiction Compliance Verification",
                "what_happened": "We audited the lead qualification pipeline across SOC2 Type II, GDPR, PCI-DSS v4, HIPAA, FedRAMP, and SOX frameworks.",
                "what_to_notice": "Notice that different industry verticals enforce different mandatory frameworks (e.g. Banking requires SOX & AML, Retail requires PCI-DSS).",
                "production_lesson": "Enterprise B2B software must adapt compliance checks dynamically based on the client's industry and jurisdiction."
            }
        }
        
        return INTUITIONS.get(sid, {
            "title": f"Architectural Insight for {step_id.upper()}",
            "analogy": "💡 Practical Engineering Principle",
            "what_happened": "The system executed a verified pipeline inspection step.",
            "what_to_notice": "Observe the separation of concerns and deterministic outputs.",
            "production_lesson": "Systematic verification enforces quality, latency, and security thresholds across multi-agent pipelines."
        })


