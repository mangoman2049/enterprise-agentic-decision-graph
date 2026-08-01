# V3 Context Graph Visualization

This diagram represents the Institutional Memory captured by the Graph Engine. Nodes with >= 2 precedent will automatically override the Human-in-the-Loop.

```mermaid
graph TD
    classDef autoApprove fill:#d4edda,stroke:#28a745,color:#155724;
    classDef autoReject fill:#f8d7da,stroke:#dc3545,color:#721c24;
    classDef learning fill:#fff3cd,stroke:#ffc107,color:#856404;

    subgraph Institutional Memory (Context Graph)
        Node0["<b>Healthcare</b><br/><br/><i>Triggers:</i><br/>Security Blocker: GDPR Data Residency: EU region deployment required (Not supported yet)<br/>---<br/><b>AUTO-REJECT (Precedent: 5)</b>"]:::autoReject
        Node1["<b>Finance</b><br/><br/><i>Triggers:</i><br/>Deal > $250k (Strategic)<br/>---<br/><b>AUTO-APPROVE (Precedent: 2)</b>"]:::autoApprove
        Node2["<b>Healthcare</b><br/><br/><i>Triggers:</i><br/>Security Blocker: GDPR Data Residency: EU region deployment required (Not supported yet), HIPAA: BAA signing required<br/>---<br/><b>AUTO-REJECT (Precedent: 2)</b>"]:::autoReject
    end
```