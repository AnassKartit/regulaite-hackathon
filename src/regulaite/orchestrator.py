from regulaite.agents.discovery_agent import DiscoveryAgent
from regulaite.agents.policy_agent import PolicyAgent
from regulaite.agents.documentation_agent import DocumentationAgent

class Orchestrator:
    def __init__(self, repo=None):
        self.discovery_agent = DiscoveryAgent(repo)
        self.policy_agent = PolicyAgent()
        self.documentation_agent = DocumentationAgent()

    def run(self):
        # Discover assets
        assets = self.discovery_agent.discover()
        
        # Analyze each asset
        reports = []
        for asset in assets:
            report = self.policy_agent.analyse(asset)
            reports.append(report)
            
        # Generate documentation
        pdf_path = self.documentation_agent.generate(reports)
        
        return {
            "assets": [a.model_dump() for a in assets],
            "reports": [r.model_dump() for r in reports],
            "pdf": pdf_path
        }