# Foundation Concepts: Agent-to-Agent (A2A) Communication

## What is A2A?

**Agent-to-Agent (A2A)** is a structured communication protocol that enables agents to discover, authenticate, and exchange messages with each other. Unlike simple function calls, A2A provides:

- **Agent Cards**: Each agent publishes a card with its name, role, capabilities, and protocol version
- **Structured payloads**: Messages have typed schemas, not arbitrary strings
- **Traceability**: Every message has sender, receiver, payload size, and timestamp
- **Discoverability**: Agents can find and invoke other agents dynamically

## A2A in Our System

Our implementation follows A2A conventions (agent cards with `name/role/protocol`, structured message passing via the orchestrator) but uses **in-process Python calls** rather than network HTTP.

In production A2A, each agent would be a **separate service** with its own endpoint, discoverable via agent cards published to a registry.

### Agent Card Example
```python
# From agents/base_agent.py
self.agent_card = {
    "name": "researcher",
    "role": "Enriches lead with CRM and public data.",
    "protocol": "a2a/2.0"
}
```

## Communication Trace Example

Processing: **FinTrust Bank (Finance, $500K budget)**

| Step | From | To | Payload | Size | Protocol |
|------|------|----|---------|------|----------|
| 1 | Orchestrator | Lead Intake Agent | Raw lead JSON: {company, industry, budget, pain_points} | 245 bytes | A2A |
| 2 | Lead Intake Agent | Research Agent | Structured: {company: 'FinTrust Bank', urgency: 'High'} | 180 bytes | A2A |
| 3 | Research Agent | CRM MCP Server | Tool call: `lookup_account(company_name='FinTrust Bank')` | 62 bytes | MCP/stdio |
| 4 | CRM MCP Server | Research Agent | Response: {status: 'Prospect', last_contact: '2023-10-01'} | 95 bytes | MCP/stdio |
| 5 | Research Agent | Qualification Agent | Enriched lead: {crm_status: 'Prospect', revenue: 500000} | 210 bytes | A2A |
| 6 | Qualification Agent | Orchestrator | Qualified: True, score: 82/100 | 45 bytes | A2A |
| 7 | Orchestrator | [Product Fit ∥ Security ∥ Commercial] | Parallel fan-out: Full enriched lead context | 3 × 420 bytes | A2A |
| 8 | [Product Fit + Security + Commercial] | HITL Gate | Aggregated: {fit: 'Strong', security: 'Pass', arr: $470K} | 380 bytes | A2A |

**Key observation**: Steps 3-4 cross the A2A/MCP boundary :  the Research Agent makes an A2A-to-MCP call to the CRM server.

## Parallel Fan-Out Pattern

The Orchestrator uses `asyncio.gather()` to fan-out to 3 agents simultaneously:
```python
product_task = asyncio.create_task(self.product.process(lead))
security_task = asyncio.create_task(self.security.process(lead))
commercial_task = asyncio.create_task(self.commercial.process(lead))

product_res, security_res, commercial_res = await asyncio.gather(
    product_task, security_task, commercial_task
)
```

This reduces wall-clock time from ~600ms (sequential) to ~200ms (parallel).

## Code Reference
- `agents/base_agent.py` :  Agent card definition and A2A wrapper
- `orchestrator/workflow_engine.py` :  Orchestrator message routing
