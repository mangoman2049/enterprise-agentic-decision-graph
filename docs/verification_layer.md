# Day 5 Independent Verification Layer: Deterministic Proof Hierarchy

Version: 1.0 (Week 1 :  Evals & Verification)  
Focus: Implementing deterministic `Claim ➔ Evidence ➔ Freshness ➔ Policy ➔ Decision` verification that overrides LLM consensus.

---

## 1. The Core Verification Fallacy
A common vulnerability in multi-agent architectures is **LLM Agreement Bias**: using a second LLM ("LLM-as-a-Judge") to verify the first LLM's output. If both models share identical training biases or read the same hallucinated context, they will agree with 100% confidence while being 100% wrong!

To achieve genuine enterprise-grade reliability, the Independent Verifier uses **deterministic code rules and authoritative database facts ahead of LLM agreement**.

---

## 2. The 5-Step Verification Hierarchy

```
[Agent Output Recommendation]
              │
              ▼
   ┌──────────────────────┐
   │ 1. Claim Extraction  │ ──► Extract atomic factual claims made by agent
   └──────────────────────┘
              │
              ▼
   ┌──────────────────────┐
   │ 2. Evidence Mapping  │ ──► Verify each claim maps to retrieved MCP source evidence
   └──────────────────────┘
              │
              ▼
   ┌──────────────────────┐
   │ 3. Freshness Check   │ ──► Verify source evidence timestamp is $\le 365$ days old
   └──────────────────────┘
              │
              ▼
   ┌──────────────────────┐
   │ 4. Policy Rules Check│ ──► Enforce hard corporate policy boundaries (e.g. ARR, SOC2, HIPAA)
   └──────────────────────┘
              │
              ▼
   ┌──────────────────────┐
   │ 5. Decision Verdict  │ ──► VERIFIED | ABSTAIN | ESCALATE_UNSUPPORTED
   └──────────────────────┘
```

---

## 3. Verification Rules Engine

1. **Rule V-1 (Claim-to-Evidence Grounding)**: Every claim made by the Qualification or Product Fit Agent must have a direct matching string in the retrieved CRM or KB MCP response payload. If unevidenced claims are detected $\implies$ Verdict: `ESCALATE_UNSUPPORTED`.
2. **Rule V-2 (Evidence Freshness)**: Evidence from CRM last updated prior to 2023-01-01 is flagged as `STALE_EVIDENCE` $\implies$ Verdict: `ABSTAIN_STALE_DATA`.
3. **Rule V-3 (Deterministic Policy Safety Net)**: 
   - If `industry == "Healthcare"` AND `hipaa_required == True` AND `security_pass == False` $\implies$ Decision MUST be `REJECTED`. If agent outputs `APPROVED` $\implies$ Override Verdict: `FORCE_REJECT`.
   - If `arr > $250,000` $\implies$ Decision MUST pass through HITL Escalation Queue. If agent attempts `AUTO_APPROVE` $\implies$ Override Verdict: `FORCE_ESCALATE`.

---

## 4. Verification Layer Output Matrix

| Case Scenario | Agent Proposed Verdict | Verifier Check Result | Verifier Override Verdict | Reason / Rule Triggered |
| :--- | :--- | :--- | :--- | :--- |
| `FinTrust Bank` | Approved | PASSED | **APPROVED (Verified)** | All claims grounded; SOC2 active. |
| `Legacy Retail` | Approved | FAILED (Stale Data) | **ABSTAIN (Stale Evidence)** | CRM data last updated 2021 (Rule V-2). |
| `Apex Logistics` | Approved | FAILED (ARR Mismatch) | **ESCALATE (Discrepancy)** | CRM ARR ($500k) != Lead ARR ($50k). |
| `Shadow Corp` | Approved | FAILED (Prompt Injection) | **FORCE_REJECT (Violation)** | Injected instruction string detected (Rule V-3). |

---

## Sign-off & Policy Approval
- **Lead Verification Engineer**: *Independent Reliability Suite*
- **Chief Compliance Officer**: *Enterprise AI Governance*
