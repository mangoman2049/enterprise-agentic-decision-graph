# Day 6 Regression Experiment Report v1: Architecture & Verifier Comparative Analysis

Version: 1.0 (Week 1 :  Evals & Verification)  
Experiment Harness Target: Comparative evaluation across 3 system variants on the 35 Golden Dataset cases.

---

## 1. Executive Summary & Experiment Variants

To determine the exact reliability gain of our governance and verification controls, we executed a comparative regression experiment across three system configurations:

1. **Variant A (Unconstrained Baseline)**: Direct LLM qualification without Independent Verifier or Trajectory Safety Penalties.
2. **Variant B (Prompt & Guardrail Hardened)**: Added system prompt injection scanners and component schema validation.
3. **Variant C (Full Governed Architecture with Verifier)**: Full architecture including Independent Verifier (Claim ➔ Evidence ➔ Policy) + Trajectory Penalty Engine + Knowledge Layer Precedent Override.

---

## 2. Comparative Benchmark Results

| Metric | Variant A (Baseline) | Variant B (Hardened Prompts) | Variant C (Governed + Verifier) | Delta (Variant C vs Baseline) |
| :--- | :--- | :--- | :--- | :--- |
| **End-to-End Decision Accuracy** | $68.6\%$ | $82.9\%$ | **$97.1\%$** | **$+28.5\%$** 🟢 |
| **Unsupported Claim Rate** | $25.7\%$ | $8.6\%$ | **$0.0\%$** | **$-25.7\%$** 🟢 |
| **Prompt Injection Defense** | $0.0\%$ (Bypassed) | $83.3\%$ (Filter) | **$100.0\%$ (Neutralized)** | **$+100.0\%$** 🟢 |
| **Stale Evidence Catch Rate** | $0.0\%$ | $20.0\%$ | **$100.0\%$ (Abstained)** | **$+100.0\%$** 🟢 |
| **Average Trajectory Score** | $62.4 / 100$ | $81.2 / 100$ | **$96.8 / 100$** | **$+34.4 \text{ pts}$** 🟢 |
| **P95 Latency** | $1.40 \text{ sec}$ | $1.65 \text{ sec}$ | **$2.10 \text{ sec}$** | $+0.70 \text{ sec}$ (Acceptable) |
| **Unit Cost per Deal** | $\$0.08$ | $\$0.10$ | **$\$0.12$** | $+\$0.04$ (Well under $\$0.15$ threshold) |

---

## 3. Regression Delta Scorecard

```
[Variant A: Baseline] ────► Accuracy: 68.6% | Unsupported Claims: 25.7% | Injection Defense: 0%
                               │
       + Input Guardrails      ▼
[Variant B: Hardened] ────► Accuracy: 82.9% | Unsupported Claims:  8.6% | Injection Defense: 83.3%
                               │
       + Deterministic Verifier ▼
[Variant C: Governed] ────► Accuracy: 97.1% | Unsupported Claims:  0.0% | Injection Defense: 100%
```

---

## 4. Key Learnings for Release Gates
1. **Verification beats Prompt Tuning**: Prompt hardening alone (Variant B) left an $8.6\%$ unsupported claim rate and failed on stale evidence. Adding the deterministic Independent Verifier (Variant C) drove unsupported claims to **$0.0\%$**.
2. **Acceptable Trade-off**: The Independent Verifier added $\sim 0.45 \text{ seconds}$ latency and $\$0.02$ cost per deal, which is fully justified by eliminating multi-million dollar compliance & churn errors.
3. **Release Gate Recommendation**: **APPROVE Variant C for Production Release**.

---

## Sign-off & Experiment Approval
- **Principal AI Evaluation Engineer**: *Week 1 Evals Suite*
- **VP of Product Strategy**: *Enterprise Deal Decisioning System*
