import asyncio
import json
import os
import sys

from fastmcp import Client
from orchestrator.workflow_engine import WorkflowEngine
from knowledge_graph.knowledge_graph import KnowledgeGraphEngine

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

async def run_phase(engine, leads, phase_name, phase_id):
    print(f"\n{'='*60}")
    print(f" 🚀 {phase_name} ")
    print(f"{'='*60}\n")
    
    results = []
    for lead in leads:
        print("-" * 60)
        result = await engine.process_lead(lead, phase=phase_id)
        results.append((lead['company'], result['status'], result.get('arr', 0)))
        
    print("\n=========================================================")
    print(f" 📊 {phase_name} DASHBOARD")
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


async def main():
    print("=========================================================")
    print(" 🧠 V5 ENTERPRISE KNOWLEDGE LAYER SIMULATION")
    print("=========================================================\n")
    
    knowledge_graph = KnowledgeGraphEngine()
    
    base_dir = os.path.dirname(__file__)
    crm_path = os.path.join(base_dir, "mcp_servers", "crm_mcp.py")
    kb_path = os.path.join(base_dir, "mcp_servers", "kb_mcp.py")
    sec_path = os.path.join(base_dir, "mcp_servers", "security_mcp.py")
    
    p1_path = os.path.join(base_dir, "phase1_training.json")
    p2_path = os.path.join(base_dir, "phase2_testing.json")
        
    with open(p1_path, "r", encoding="utf-8") as f:
        p1_leads = json.load(f)
    with open(p2_path, "r", encoding="utf-8") as f:
        p2_leads = json.load(f)
        
    print("🔌 Booting Enterprise MCP Servers (CRM, KB, Security)...")
    async with Client(crm_path) as crm_client, \
               Client(kb_path) as kb_client, \
               Client(sec_path) as sec_client:
        
        print("✅ Servers online. Booting Orchestrator...")
        engine = WorkflowEngine(crm_client, kb_client, sec_client, knowledge_graph)
        
        # ── PHASE 1: Training & Outcomes ──
        print("\n⏳ [SIMULATING 6 MONTHS OF HISTORICAL DATA]")
        print("   In Phase 1, the human makes some good and bad decisions.")
        print("   The Knowledge Graph tracks the ultimate OUTCOMES (Churn vs Renewal).")
        await run_phase(engine, p1_leads, "PHASE 1: HISTORICAL TRAINING", "P1")
        
        print("\n⏳ ... Time Passes ... 6 Months Later ...\n")
        
        # ── PHASE 2: Live Testing ──
        print("🌍 [LIVE ENVIRONMENT]")
        print("   Now, processing fresh leads. The Knowledge Graph will warn you")
        print("   if you try to repeat a mistake that previously led to Churn.")
        await run_phase(engine, p2_leads, "PHASE 2: LIVE KNOWLEDGE GRAPH", "P2")

if __name__ == "__main__":
    asyncio.run(main())
