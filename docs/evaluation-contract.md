# Evaluation Contract: Governed Enterprise Deal Decisioning System

Version: 1.0 (Week 1 — Evals & Verification)  
System Target: Multi-Agent A2A Lead Qualification & Deal Approval Engine  

---

## Executive Overview
This Evaluation Contract establishes the formal quality, safety, and operational standards for the Governed Enterprise Deal Decisioning System. Moving beyond subjective human assessment ("the demo appears to work"), this contract defines four explicit metric classes with mathematical formulas, strict acceptance thresholds, assigned operational owners, and explicit failure consequences.

---

## 1. Metric Class 1: Business Outcome Metrics
*Focus: Measuring direct commercial value, revenue preservation, and risk-adjusted business impact.*

| Metric Name | Formula / Measurement | Target Threshold | Operational Owner | Failure Consequence |
| :--- | :--- | :--- | :--- | :--- |
| **Decision Accuracy** | $\frac{\text{Correct Qualification Decisions}}{\text{Total Evaluated Leads}} \times 100\%$ | $\ge 92.0\%$ | DVP of Sales Operations | Automatic halt of auto-approval thresholds; mandatory human escalation fallback. |
| **Churn Prevention Rate** | $1 - \frac{\text{Approved Deals that Churn within 6 Mo.}}{\text{Total Approved Deals}}$ | $\ge 95.0\%$ | Head of Customer Success | System invalidates past precedent rules for target customer segment in Knowledge Graph. |
| **Revenue Preservation Ratio** | $\frac{\text{ARR of Correctly Qualified Deals}}{\text{Total Pipeline ARR}}$ | $\ge 90.0\%$ | VP of Revenue Strategy | Escalation threshold lowered from $250k to $100k for all strategic deals. |

---

## 2. Metric Class 2: Agent Quality Metrics
*Focus: Assessing structural correctness, reasoning groundedness, schema compliance, and tool efficiency.*

| Metric Name | Formula / Measurement | Target Threshold | Operational Owner | Failure Consequence |
| :--- | :--- | :--- | :--- | :--- |
| **Schema Compliance** | $\frac{\text{Valid JSON Outputs Matching Contract}}{\text{Total Agent Output Steps}}$ | $100\%$ | AI Lead Engineer | Immediate agent step retry with schema error feedback payload. |
| **Claim Groundedness** | $\frac{\text{Extracted Claims Supported by Source Evidence}}{\text{Total Claims Made}}$ | $100\%$ | Lead NLP / Verification Eng. | Independent Verifier flags claim as "Unevidenced" and forces human review. |
| **Tool Calling Accuracy** | $\frac{\text{Valid MCP Tool Calls with Correct Parameters}}{\text{Total MCP Invocations}}$ | $\ge 98.0\%$ | Platform Integration Architect | MCP server circuit breaker trips; fallback to static cached CRM schema. |

---

## 3. Metric Class 3: System Performance & Cost Metrics
*Focus: Controlling operational latency, token consumption, and unit economics.*

| Metric Name | Formula / Measurement | Target Threshold | Operational Owner | Failure Consequence |
| :--- | :--- | :--- | :--- | :--- |
| **End-to-End Latency** | P95 time from Lead Intake to Final Qualification | $\le 2.50 \text{ seconds}$ | Platform Reliability Engineer | Parallel DAG execution timeout enforced; non-critical agents skipped. |
| **Token Efficiency** | $\frac{\text{Useful Information Tokens}}{\text{Total Inbound + Outbound Tokens}}$ | $\ge 85.0\%$ | AI Platform Architect | Prompt context truncation enforced; agent system prompt shortened. |
| **Cost per Qualified Deal** | $\frac{\text{Total Inference + MCP Execution Cost}}{\text{Successfully Qualified Deals}}$ | $\le \$0.15 \text{ / deal}$ | AI Commercial Leader | Routing engine switches to lightweight/cheaper model tier. |

---

## 4. Metric Class 4: Governance & Safety Metrics
*Focus: Enforcing regulatory compliance, PII protection, policy sequence integrity, and zero unauthorized actions.*

| Metric Name | Formula / Measurement | Target Threshold | Operational Owner | Failure Consequence |
| :--- | :--- | :--- | :--- | :--- |
| **Unsupported Claim Rate** | $\frac{\text{Decisions Containing Unevidenced Claims}}{\text{Total Executed Decisions}}$ | $0.0\%$ | Chief Risk & Compliance Officer | Hard stop: Independent Verifier issues automatic REJECT / ESCALATE verdict. |
| **High-Risk False Approval Rate** | $\frac{\text{Non-compliant High-Risk Deals Approved}}{\text{Total High-Risk Cases}}$ | $0.0\%$ | VP of Enterprise Security | Emergency Write Kill-Switch activated; all HITL auto-approvals suspended. |
| **Policy Sequence Integrity** | $\frac{\text{Executions Following Required DAG Order}}{\text{Total Workflow Executions}}$ | $100\%$ | Governance Lead | Workflow orchestrator aborts execution; flags trajectory anomaly. |

---

## Verification & Failure Escalation Matrix

```
[Agent Execution] ──► [Component Evals] ──► [Trajectory Scorecard] ──► [Independent Verifier]
                              │                          │                           │
                   Fail: Component Retry       Fail: Path Penalty          Fail: Hard Abstain/Escalate
                              │                          │                           │
                              ▼                          ▼                           ▼
                     [System Log & Trace]     [Governance Alert]           [DVP HITL Queue]
```

### Sign-off & Contract Ownership
- **Lead AI Platform Product Manager**: *Manish Pandey*
- **Head of AI Engineering**: *Enterprise AI Team*
- **Effective Date**: August 2026
