import json
import random
import os

def generate_datasets():
    """Generates two datasets: Phase 1 (Training with Outcomes) and Phase 2 (Testing)."""
    
    # We will simulate a specific mistake: Approving Tech startups missing On-Premises.
    # We will simulate these being approved by humans in Phase 1, but they ALL Churn.
    
    patterns = [
        # Pattern 1: Finance + Missing SOC2 + >$250k (The "Strategic Finance Exception") - Usually Renews
        {"name": "FinTrust Bank", "industry": "Finance", "country": "US", "budget": 600000, "soc2_required": True, "churn_rate": 0.1},
        
        # Pattern 2: Healthcare + Missing GDPR (Data Residency) (The "Hard No" pattern) - Doesn't matter, we reject.
        {"name": "NovaHealth", "industry": "Healthcare", "country": "UK", "budget": 150000, "soc2_required": False, "churn_rate": 0.5},
        
        # Pattern 3: Tech + Missing On-Prem Feature + <$100k (The "Mistake" pattern) - ALWAYS CHURNS
        {"name": "Stealth AI", "industry": "Technology", "country": "US", "budget": 50000, "soc2_required": False, "pain": "Requires On-Premises", "churn_rate": 1.0},
        
        # Standard easy wins (No HITL) - Usually Renews
        {"name": "RetailGiant", "industry": "Retail", "country": "US", "budget": 50000, "soc2_required": False, "churn_rate": 0.05}
    ]

    def create_lead(i, pattern, phase):
        employees = int(pattern["budget"] / 100)
        revenue = employees * random.randint(100000, 500000)
        
        pain_points = ["High latency", "Poor UX"]
        if "pain" in pattern:
            pain_points.append(pattern["pain"])
            
        security = {
            "soc2_required": pattern.get("soc2_required", False),
            "hipaa_required": pattern["industry"] == "Healthcare",
            "gdpr_required": pattern["country"] in ["UK", "DE"],
            "data_residency": pattern["country"]
        }
        
        lead = {
            "lead_id": f"L-{phase}-{i+1000}",
            "company": f"{pattern['name']} - Div {i}",
            "industry": pattern["industry"],
            "country": pattern["country"],
            "raw_employees": employees,
            "raw_revenue": revenue,
            "current_vendor": "NICE",
            "pain_points": pain_points,
            "budget": pattern["budget"],
            "timeline": "1 month", 
            "security_needs": security
        }
        
        # For Phase 1, we embed the "future outcome" (churn vs renew) directly into the lead data
        # so the simulation runner knows what happens 6 months later.
        if phase == "P1":
            # Determine outcome based on churn rate
            if random.random() < pattern["churn_rate"]:
                lead["_simulated_outcome"] = "Churned"
            else:
                lead["_simulated_outcome"] = "Renewed"
                
        return lead

    # Phase 1: Training Data (30 leads)
    p1_leads = []
    for i in range(30):
        base = patterns[i % len(patterns)]
        p1_leads.append(create_lead(i, base, "P1"))
        
    # Phase 2: Testing Data (10 leads)
    p2_leads = []
    for i in range(10):
        base = patterns[i % len(patterns)]
        p2_leads.append(create_lead(i, base, "P2"))
        
    base_dir = os.path.dirname(__file__)
    
    with open(os.path.join(base_dir, "phase1_training.json"), "w", encoding="utf-8") as f:
        json.dump(p1_leads, f, indent=4)
        
    with open(os.path.join(base_dir, "phase2_testing.json"), "w", encoding="utf-8") as f:
        json.dump(p2_leads, f, indent=4)
        
    print("✅ Generated V5 Datasets: phase1_training.json and phase2_testing.json")

if __name__ == "__main__":
    generate_datasets()
