# Foundation Concepts: MCP Servers, Skills & Tools

## What is MCP?

**Model Context Protocol (MCP)** is a standardized interface between AI agents and external data sources. Think of it as the **API gateway pattern for AI agents**.

Key benefits:
- **Decoupling**: Swap Salesforce for HubSpot without changing agent code
- **Typed tools**: Each tool has a defined schema (parameters, return types)
- **Transport flexibility**: Run locally (stdio) or over network (SSE, HTTP)

## MCP Servers in This System

### 1. CRM Server (`mcp_servers/crm_mcp.py`)
- **Transport**: stdio (subprocess, stdin/stdout pipes)
- **Framework**: FastMCP 3.x
- **Tools**:
  | Tool | Parameters | Returns | Used By |
  |------|-----------|---------|---------|
  | `lookup_account` | `company_name: str` | Account status, last contact, owner | Research Agent |
  | `get_past_opportunities` | `company_name: str` | Past deal count, win/loss, total value | Research Agent |

### 2. Knowledge Base Server (`mcp_servers/kb_mcp.py`)
- **Transport**: stdio
- **Tools**:
  | Tool | Parameters | Returns | Used By |
  |------|-----------|---------|---------|
  | `check_product_fit` | `industry: str, pain_points: list` | Fit score, missing features | Product Fit Agent |
  | `check_roadmap_eta` | `feature: str` | Feature availability ETA | Product Fit Agent |

### 3. Security Server (`mcp_servers/security_mcp.py`)
- **Transport**: stdio
- **Tools**:
  | Tool | Parameters | Returns | Used By |
  |------|-----------|---------|---------|
  | `check_compliance` | `industry: str, requirements: dict` | SOC2/GDPR/HIPAA status | Security Agent |

## How Tool Selection Works

In our simulation, each agent has a **hardcoded tool mapping** (Research Agent always calls `lookup_account`). In a production LLM-powered agent, the model receives the tool schema and **decides which tool to call** based on the task context — this is called **"tool use"** or **"function calling"**.

## Transport Options

| Transport | Use Case | How It Works |
|-----------|----------|--------------|
| **stdio** | Local/dev | MCP server runs as subprocess, communicates via stdin/stdout |
| **SSE** | Network | Server-Sent Events over HTTP for real-time streaming |
| **HTTP** | Production | Standard HTTP request/response for network-distributed servers |

## Code Reference
- `mcp_servers/crm_mcp.py` — CRM MCP server implementation
- `mcp_servers/kb_mcp.py` — Knowledge Base MCP server
- `mcp_servers/security_mcp.py` — Security compliance MCP server
