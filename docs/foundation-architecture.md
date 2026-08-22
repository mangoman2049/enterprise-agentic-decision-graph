# Foundation Concepts: Multi-Agent Architecture

## Why Multiple Agents?

In enterprise AI systems, a **single monolithic agent** with multiple tools creates:
- A massive prompt with conflicting objectives
- No way to isolate which "skill" failed during evaluation
- A single error boundary where one failure crashes everything

**Multi-agent architecture** provides:
- **Separation of concerns**: Each agent has a focused prompt and responsibility
- **Independent evaluation**: Test and replace agents individually
- **Error isolation**: One agent's failure doesn't cascade to others
- **Parallel execution**: Independent agents run simultaneously

## Agent Registry

| Agent | Role | MCP Tools | Receives From | Sends To |
|-------|------|-----------|---------------|----------|
| Lead Intake | Extracts and normalizes raw lead data | None | Inbound Lead JSON | Research Agent |
| Research | Enriches lead with CRM history | `lookup_account`, `get_past_opportunities` | Lead Intake Agent | Qualification Agent |
| Qualification | Scores firmographic fit | None | Research Agent | Product Fit / Security / Commercial |
| Product Fit | Matches product features to pain points | `check_product_fit`, `check_roadmap_eta` | Qualification Agent | HITL Gate |
| Security | Validates compliance (SOC2, GDPR, HIPAA) | `check_compliance` | Qualification Agent | HITL Gate |
| Commercial | Calculates ARR and pricing tier | None | Qualification Agent | HITL Gate |
| HITL Gate | Routes to auto-decision or human escalation | None | Product Fit + Security + Commercial | DVP Sales |

## DAG Flow

```
Intake → Research → Qualification → [Product Fit ∥ Security ∥ Commercial] → HITL Gate
```

The `∥` symbol indicates **parallel execution** :  these agents run simultaneously using `asyncio.gather()`.

## Key Design Decisions

### Why run Product Fit, Security, and Commercial in parallel?
These three evaluations are independent :  none depends on the other's output. Running them with `asyncio.gather()` cuts latency by ~66% compared to sequential execution.

### What happens if Qualification disqualifies a lead?
The orchestrator **short-circuits** immediately. Product Fit, Security, and Commercial are never invoked, saving compute cost and latency. This is called "early exit" or "fail-fast" routing.

## Code Reference
- `orchestrator/workflow_engine.py` :  The main DAG orchestrator
- `agents/base_agent.py` :  Base class with OpenTelemetry tracing
- `agents/*.py` :  Individual agent implementations
