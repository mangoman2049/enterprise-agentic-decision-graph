# Foundation Concepts: Enterprise Knowledge Graph & Self-Learning

## What is the Knowledge Graph?

The **Knowledge Graph** is the system's memory. It stores outcomes of past decisions (approved, rejected, churned) as **nodes and edges** in a NetworkX graph, enabling the system to:

- **Learn from experience**: Every deal outcome strengthens or weakens decision patterns
- **Surface warnings**: Similar past failures trigger escalation warnings
- **Enable auto-approval**: High-confidence patterns bypass human review

## How It Works

### Phase 1: Training (Historical Data)
During startup, the system processes ~30 historical leads across 3 quarters. Each outcome is stored as a graph relationship:

```
[Industry: Finance] --has_lead--> [FinTrust Bank] --outcome--> [APPROVED]
[Industry: Technology] --has_lead--> [Stealth AI] --outcome--> [CHURNED]
```

### Phase 2: Live Inference
When a new lead arrives, the HITL Gate queries the graph:

1. **Find similar past leads** (matching on industry + pain points + deal size)
2. **Calculate pattern confidence** (what % of similar leads succeeded/failed?)
3. **Surface warnings** if churn/rejection rate exceeds threshold

## Learning Example

### Scenario
Stealth AI (Technology) was approved in Q1 but churned within 90 days due to missing on-premises feature.

### Graph Action
Knowledge Graph stored:
```
Industry=Technology + PainPoint=On-Premises → Outcome=CHURNED
```

### Future Impact
When a new Technology lead with on-premises needs arrives, the HITL Gate surfaces:
> 🚨 **Knowledge Layer Warning**: Similar leads in Technology with on-premises requirements have 73% churn rate. Recommend escalation.

## How is this different from a Rules Engine?

| Feature | Rules Engine | Knowledge Graph |
|---------|-------------|-----------------|
| Rule creation | Manual IF-THEN by humans | Automatic from outcomes |
| Adaptability | Requires manual updates | Self-learning |
| Coverage | Only anticipated scenarios | Discovers patterns automatically |
| Confidence | Binary (rule fires or not) | Probabilistic (% confidence) |

## Graph Node Types

- **Industry nodes**: Finance, Healthcare, Technology, Retail
- **Company nodes**: Individual lead companies
- **Outcome nodes**: APPROVED, REJECTED, CHURNED, ESCALATED
- **Pain Point nodes**: Specific customer needs
- **Edge types**: `has_lead`, `outcome`, `similar_to`, `warned_about`

## What Triggers a Warning?

The HITL Gate queries the graph when:
- Matching leads have a **churn rate > 50%**
- Matching leads have a **rejection rate > 60%**
- The lead's pain points match a known **churned pattern**

## Can the Knowledge Graph Be Wrong?

**Yes!** This is exactly why we need the **Independent Verifier** (Week 1, Step 5). The graph learns from historical data which may be **biased or outdated**. The Verifier adds a deterministic safety net that checks freshness and evidence quality before trusting graph-derived recommendations.

## Code Reference
- `knowledge_graph/knowledge_graph.py` — NetworkX graph implementation
- `hitl/human_approval.py` — HITL Gate with graph querying
- `enterprise_brain.html` — Interactive D3.js graph visualization
