import os
import json
import networkx as nx

_CACHED_GRAPH_HTML: str | None = None

def get_interactive_graph_html(force_refresh: bool = False) -> str:
    global _CACHED_GRAPH_HTML
    if _CACHED_GRAPH_HTML is not None and not force_refresh:
        return _CACHED_GRAPH_HTML
        
    base_dir = os.path.dirname(__file__)
    
    from knowledge_graph.knowledge_graph import KnowledgeGraphEngine
    kg = KnowledgeGraphEngine()
    
    with open(os.path.join(base_dir, "phase1_training.json"), "r", encoding="utf-8") as f:
        p1_leads = json.load(f)
        
    for lead in p1_leads:
        reasons = []
        if lead['budget'] > 250000: reasons.append("Deal > $250k (Strategic)")
        if lead['industry'] == "Healthcare": reasons.append("Security Blocker: ['GDPR Data Residency']")
        if lead.get('pain') == "Requires On-Premises": reasons.append("Weak Product Fit: ['On-Premises']")
        
        decision = "approved" if lead['industry'] != "Healthcare" else "rejected"
        outcome = lead.get("_simulated_outcome")
        kg.record_decision(lead, reasons, decision, outcome)
        
    nodes = []
    edges = []
    
    for node_id, data in kg.graph.nodes(data=True):
        ntype = data.get("type", "Account")
        label = data.get("label", str(node_id))
        
        # Color mapping aligned with light enterprise palette
        if ntype == "Outcome":
            color = "#059669" if "RENEWED" in label else "#DC2626"
            group = "Outcome"
        elif ntype == "Decision":
            color = "#4F46E5" if "APPROVE" in label else "#64748B"
            group = "Decision"
        elif ntype == "Policy":
            color = "#D97706"
            group = "Policy"
        else:
            color = "#0284C7"
            group = "Lead / Company"
            
        nodes.append({
            "id": str(node_id),
            "label": label,
            "type": ntype,
            "color": color,
            "group": group
        })
        
    for source, target, data in kg.graph.edges(data=True):
        weight = data.get("weight", 1)
        edges.append({
            "source": str(source),
            "target": str(target),
            "weight": weight
        })
        
    graph_payload = json.dumps({"nodes": nodes, "edges": edges})
    
    html_template = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Enterprise Brain Knowledge Graph</title>
    <!-- Google tag (gtag.js) -->
    <script async src="https://www.googletagmanager.com/gtag/js?id=G-M7C90S8YYC"></script>
    <script>
      window.dataLayer = window.dataLayer || [];
      function gtag(){{dataLayer.push(arguments);}}
      gtag('js', new Date());

      gtag('config', 'G-M7C90S8YYC', {{
        page_title: 'Enterprise Brain Knowledge Graph',
        send_page_view: true
      }});
    </script>
    <script src="https://d3js.org/d3.v7.min.js"></script>
    <style>
        * {{ box-sizing: border-box; margin: 0; padding: 0; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; }}
        body {{ background: #FAFAFA; color: #0F172A; overflow: hidden; height: 100vh; display: flex; flex-direction: column; }}
        .header {{ display: flex; justify-content: space-between; align-items: center; padding: 12px 16px; background: #FFFFFF; border-bottom: 1px solid #E2E8F0; z-index: 10; }}
        .title {{ font-size: 13px; font-weight: 600; color: #1E293B; }}
        .legend {{ display: flex; gap: 14px; font-size: 11px; align-items: center; }}
        .legend-item {{ display: flex; align-items: center; gap: 6px; }}
        .dot {{ width: 10px; height: 10px; border-radius: 50%; display: inline-block; }}
        .controls {{ display: flex; gap: 6px; }}
        .btn {{ background: #FFFFFF; border: 1px solid #CBD5E1; color: #334155; padding: 4px 10px; border-radius: 6px; font-size: 12px; cursor: pointer; font-weight: 500; transition: all 0.15s; }}
        .btn:hover {{ background: #F1F5F9; border-color: #94A3B8; }}
        #graph-container {{ flex: 1; position: relative; width: 100%; height: 100%; }}
        svg {{ width: 100%; height: 100%; cursor: grab; }}
        svg:active {{ cursor: grabbing; }}
        .node {{ stroke: #FFFFFF; stroke-width: 2px; cursor: pointer; transition: r 0.2s; }}
        .node:hover {{ stroke: #4F46E5; stroke-width: 3px; }}
        .node-label {{ font-size: 10px; fill: #1E293B; pointer-events: none; text-anchor: middle; font-weight: 500; }}
        .link {{ stroke: #CBD5E1; stroke-opacity: 0.6; stroke-width: 1.5px; }}
        #detail-card {{ position: absolute; bottom: 16px; right: 16px; width: 280px; background: #FFFFFF; border: 1px solid #E2E8F0; border-radius: 8px; padding: 14px; box-shadow: 0 4px 12px rgba(0,0,0,0.06); display: none; font-size: 12px; }}
        #detail-card h4 {{ font-size: 13px; margin-bottom: 6px; color: #0F172A; }}
    </style>
</head>
<body>
    <div class="header">
        <div class="title">🧠 Enterprise Brain Knowledge Graph (Phase 1 Learned Memory)</div>
        <div class="legend">
            <div class="legend-item"><span class="dot" style="background: #0284C7;"></span> Company Deals</div>
            <div class="legend-item"><span class="dot" style="background: #D97706;"></span> Governance Policy</div>
            <div class="legend-item"><span class="dot" style="background: #059669;"></span> Renewed / Won</div>
            <div class="legend-item"><span class="dot" style="background: #DC2626;"></span> Churned / High Risk</div>
        </div>
        <div class="controls">
            <button class="btn" onclick="zoomIn()">+ Zoom In</button>
            <button class="btn" onclick="zoomOut()">- Zoom Out</button>
            <button class="btn" onclick="resetZoom()">⊙ Reset</button>
        </div>
    </div>

    <div id="graph-container">
        <svg id="graph-svg"></svg>
        <div id="detail-card">
            <h4 id="card-title">Node Details</h4>
            <div id="card-body" style="color: #64748B; margin-top: 4px; line-height: 1.4;">Click any node to inspect learned relationships.</div>
        </div>
    </div>

    <script>
        const data = {graph_payload};
        const svg = d3.select("#graph-svg");
        const width = window.innerWidth;
        const height = window.innerHeight - 50;

        const g = svg.append("g");
        const zoom = d3.zoom().scaleExtent([0.2, 4]).on("zoom", (e) => g.attr("transform", e.transform));
        svg.call(zoom);

        const simulation = d3.forceSimulation(data.nodes)
            .force("link", d3.forceLink(data.edges).id(d => d.id).distance(70))
            .force("charge", d3.forceManyBody().strength(-220))
            .force("center", d3.forceCenter(width / 2, height / 2))
            .force("collision", d3.forceCollide().radius(25));

        const link = g.append("g")
            .selectAll("line")
            .data(data.edges)
            .join("line")
            .attr("class", "link")
            .attr("stroke-width", d => Math.min(d.weight * 1.5, 4));

        const node = g.append("g")
            .selectAll("circle")
            .data(data.nodes)
            .join("circle")
            .attr("class", "node")
            .attr("r", d => d.type === "Policy" ? 14 : d.type === "Outcome" ? 12 : 10)
            .attr("fill", d => d.color)
            .call(d3.drag()
                .on("start", dragstarted)
                .on("drag", dragged)
                .on("end", dragended))
            .on("click", (e, d) => showDetails(d));

        const label = g.append("g")
            .selectAll("text")
            .data(data.nodes)
            .join("text")
            .attr("class", "node-label")
            .attr("dy", 18)
            .text(d => d.label.length > 18 ? d.label.substring(0, 16) + "..." : d.label);

        simulation.on("tick", () => {{
            link.attr("x1", d => d.source.x).attr("y1", d => d.source.y)
                .attr("x2", d => d.target.x).attr("y2", d => d.target.y);
            node.attr("cx", d => d.x).attr("cy", d => d.y);
            label.attr("x", d => d.x).attr("y", d => d.y);
        }});

        function dragstarted(event) {{
            if (!event.active) simulation.alphaTarget(0.3).restart();
            event.subject.fx = event.subject.x;
            event.subject.fy = event.subject.y;
        }}
        function dragged(event) {{
            event.subject.fx = event.x;
            event.subject.fy = event.y;
        }}
        function dragended(event) {{
            if (!event.active) simulation.alphaTarget(0);
            event.subject.fx = null;
            event.subject.fy = null;
        }}

        function zoomIn() {{ svg.transition().call(zoom.scaleBy, 1.3); }}
        function zoomOut() {{ svg.transition().call(zoom.scaleBy, 0.7); }}
        function resetZoom() {{ svg.transition().call(zoom.transform, d3.zoomIdentity); }}

        function showDetails(d) {{
            const card = document.getElementById("detail-card");
            card.style.display = "block";
            document.getElementById("card-title").innerText = d.label;
            document.getElementById("card-body").innerHTML = `
                <div><strong>Category:</strong> ${{d.group}}</div>
                <div style="margin-top: 4px;"><strong>Node ID:</strong> <span style="font-family: monospace;">${{d.id}}</span></div>
                <div style="margin-top: 6px; font-size: 11px; color: #475569;">Learned graph memory node connected across ${{data.edges.filter(e => e.source.id === d.id || e.target.id === d.id).length}} operational paths.</div>
            `;
        }}
    </script>
</body>
</html>"""

    _CACHED_GRAPH_HTML = html_template
    return html_template

def export_interactive_graph() -> str:
    html = get_interactive_graph_html()
    base_dir = os.path.dirname(__file__)
    out_path = os.path.join(base_dir, "enterprise_brain.html")
    try:
        if not os.path.exists(out_path):
            with open(out_path, "w", encoding="utf-8") as f:
                f.write(html)
    except Exception:
        pass
    return html

if __name__ == "__main__":
    html = get_interactive_graph_html()
    base_dir = os.path.dirname(__file__)
    out_path = os.path.join(base_dir, "enterprise_brain.html")
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"[OK] Exported Modern D3 Interactive Knowledge Graph to: {out_path}")

