import asyncio
import json
import os
import sys

from fastmcp import Client
from orchestrator.workflow_engine import WorkflowEngine
from context_graph.graph_engine import ContextGraphEngine

# ─── Fix Windows console encoding for emoji output ───
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

async def main():
    print("=========================================================")
    print(" 🤖 V3 ENTERPRISE AI: CONTEXT GRAPH & INSTITUTIONAL MEMORY")
    print("=========================================================\n")
    
    # Initialize the Context Graph Engine
    graph_engine = ContextGraphEngine(threshold=2)
    
    # Define MCP server paths
    base_dir = os.path.dirname(__file__)
    crm_path = os.path.join(base_dir, "mcp_servers", "crm_mcp.py")
    kb_path = os.path.join(base_dir, "mcp_servers", "kb_mcp.py")
    sec_path = os.path.join(base_dir, "mcp_servers", "security_mcp.py")
    
    # Load generated data
    data_path = os.path.join(base_dir, "enterprise_dataset.json")
    if not os.path.exists(data_path):
        print("❌ Dataset missing. Run data_generator.py first.")
        return
        
    with open(data_path, "r", encoding="utf-8") as f:
        leads = json.load(f)
        
    # Start MCP clients via stdio
    print("🔌 Booting Enterprise MCP Servers (CRM, KB, Security)...")
    async with Client(crm_path) as crm_client, \
               Client(kb_path) as kb_client, \
               Client(sec_path) as sec_client:
        
        print("✅ Servers online. Booting Orchestrator...")
        engine = WorkflowEngine(crm_client, kb_client, sec_client, graph_engine)
        
        results = []
        for lead in leads:
            print("-" * 60)
            result = await engine.process_lead(lead)
            results.append((lead['company'], result['status'], result.get('arr', 0)))
            
        print("\n=========================================================")
        print(" 📊 FINAL PIPELINE DASHBOARD")
        print("=========================================================")
        print(f" {'Company':<30} | {'ARR':<12} | {'Disposition'}")
        print("-" * 65)
        total_arr = 0
        for company, status, arr in results:
            arr_str = f"${arr:,}" if arr > 0 else "-"
            print(f" {company:<30} | {arr_str:<12} | {status}")
            if "Qualified" in status:
                total_arr += arr
                
        print("-" * 65)
        print(f" 💰 Total Pipeline Generated: ${total_arr:,}")
        print("=========================================================\n")
        
        # Export Graph Data
        export_path = os.path.join(base_dir, "learned_graph.json")
        graph_engine.export_graph_data(export_path)
        print(f"🧠 Context Graph saved to {export_path}")

if __name__ == "__main__":
    asyncio.run(main())
