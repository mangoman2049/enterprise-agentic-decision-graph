# Enterprise Decision Intelligence Platform (Agentic AI)

An educational simulation demonstrating how a team of specialized AI Agents can collaborate using **Agent-to-Agent (A2A)** orchestration, **MCP (Model Context Protocol)** servers, and a dynamic **Enterprise Knowledge Layer** (Context Graph) to automate and govern B2B deal qualification.

This project was built to illustrate advanced concepts in Enterprise AI beyond simple chatbots. It answers the question: *"How does an enterprise become smarter after every decision?"*

## 🧠 The Agent Graph

Instead of one massive LLM trying to do everything, this architecture uses 7 specialized agents executing in a Directed Acyclic Graph (DAG):

1. **Lead Intake Agent**: Parses raw inbound data, validates fields, and detects intent.
2. **Research Agent**: Enriches the lead with CRM data and public signals.
3. **Qualification Agent**: Applies BANT / MEDDICC scoring criteria.
4. **Product Fit Agent**: Reads the Product Knowledge Base (MCP) to match use cases and check the roadmap.
5. **Security Agent**: Checks compliance postures (SOC2, GDPR, HIPAA, Data Residency) via MCP.
6. **Commercial Agent**: Calculates Estimated ARR, expected margins, and deal risk.
7. **Human Approval Agent**: A policy-driven HITL (Human-in-the-loop) gate.

## 🏢 The MCP Servers

The agents interact with simulated Enterprise systems using FastMCP:
*   **CRM MCP**: Simulates Salesforce/HubSpot lookups.
*   **Knowledge Base MCP**: Simulates product documentation and roadmaps.
*   **Security MCP**: Simulates compliance tracking.

## 🕸️ The Enterprise Knowledge Layer (V5)

The killer feature of this repository is the **Enterprise Knowledge Layer**, built using `networkx`. 

Most agentic systems have rigid rules. But in reality, enterprise governance is a function of institutional memory and chaos (e.g., "The VP always signs a risk waiver for Finance deals over $250k"). 

This system tracks a strict ontology: `Entity ➔ Policy ➔ Decision ➔ Outcome`. 

*   **Learns Precedent**: If a human consistently overrides a rule (e.g., Approving large Finance deals missing SOC2), the system learns the "unwritten rule" and eventually begins auto-approving them.
*   **Learns from Mistakes (Outcome Tracking)**: The simulation tracks deals 6 months post-decision. If the system notices that 100% of the Tech startups we approved (despite missing a feature) ended up **Churning**, it dynamically degrades its confidence in that policy. 
*   **Dynamic Governance**: The next time that risky pattern appears, instead of auto-approving it, the system intercepts the flow and escalates it back to the human with a massive warning: `🚨 Policy Confidence Reduced: Past 7 approvals resulted in 100% CHURN.`

## 🚀 Quick Start

1. Install dependencies:
   ```bash
   pip install fastmcp opentelemetry-api opentelemetry-sdk networkx pyvis
   ```

2. Generate the dataset (Simulates Phase 1 Training and Phase 2 Testing):
   ```bash
   python data_generator.py
   ```

3. Run the two-phase simulation:
   ```bash
   python simulation_runner.py
   ```
   *Watch as the system automatically simulates 6 months of historical data, tracks churn, and then applies those lessons to the live testing environment.*

4. Visualize the Enterprise Brain:
   ```bash
   python export_graph.py
   ```
   *This generates an interactive `enterprise_brain.html` file using PyVis so you can drag and explore the ontological decision nodes.*

## 🎯 Why This Matters

This architecture ensures:
1.  **Frugality**: Simple routing rules use deterministic logic, saving expensive LLM tokens for complex analysis.
2.  **Scalability**: Agents operate in parallel via `asyncio`.
3.  **Governance**: Governance isn't bolted on; it is built into the system. The AI learns from human mistakes and adjusts its thresholds over time.
