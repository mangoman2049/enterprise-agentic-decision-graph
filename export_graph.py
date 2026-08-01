import os
import networkx as nx
from pyvis.network import Network

def export_interactive_graph():
    base_dir = os.path.dirname(__file__)
    
    # We will just run the simulation internally here in this script for the export,
    # or ideally we'd export it from the running memory. Since we didn't save the networkx graph to disk,
    # we'll tell the user that they can see it by running export_graph.py which will simulate it quickly in memory
    # and dump it.
    
    print("Exporting Enterprise Knowledge Graph to HTML...")
    
    # Run the exact same logic quickly to build the graph
    import json
    from knowledge_graph.knowledge_graph import KnowledgeGraphEngine
    kg = KnowledgeGraphEngine()
    
    with open(os.path.join(base_dir, "phase1_training.json"), "r", encoding="utf-8") as f:
        p1_leads = json.load(f)
        
    for lead in p1_leads:
        # Simulate the reasons based on the pattern
        reasons = []
        if lead['budget'] > 250000: reasons.append("Deal > $250k (Strategic)")
        if lead['industry'] == "Healthcare": reasons.append("Security Blocker: ['GDPR Data Residency']")
        if lead.get('pain') == "Requires On-Premises": reasons.append("Weak Product Fit: ['On-Premises']")
        
        decision = "approved" if lead['industry'] != "Healthcare" else "rejected"
        outcome = lead.get("_simulated_outcome")
        kg.record_decision(lead, reasons, decision, outcome)
        
    # Generate PyVis HTML
    net = Network(height="800px", width="100%", bgcolor="#222222", font_color="white", directed=True)
    
    for node, data in kg.graph.nodes(data=True):
        node_type = data.get("type", "Unknown")
        label = data.get("label", node)
        
        color = "#97c2fc" # Default blue
        if node_type == "Outcome":
            color = "#28a745" if "RENEWED" in label else "#dc3545"
        elif node_type == "Decision":
            color = "#ffc107" if "APPROVE" in label else "#6c757d"
        elif node_type == "Policy":
            color = "#fd7e14"
            
        net.add_node(node, label=label, title=node_type, color=color, shape="box" if node_type=="Policy" else "ellipse")
        
    for source, target, data in kg.graph.edges(data=True):
        weight = data.get("weight", 1)
        label = str(weight) if weight > 1 else ""
        net.add_edge(source, target, value=weight, title=f"Weight: {weight}", label=label)
        
    out_path = os.path.join(base_dir, "enterprise_brain.html")
    net.save_graph(out_path)
    print(f"✅ Exported Interactive Knowledge Graph to: {out_path}")

if __name__ == "__main__":
    export_interactive_graph()
