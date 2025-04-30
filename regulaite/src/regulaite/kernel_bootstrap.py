import os, argparse, json
import semantic_kernel as sk
from semantic_kernel import Kernel, Process
from regulaite.agents.discovery_agent     import DiscoveryAgent
from regulaite.agents.policy_agent        import PolicyAgent
from regulaite.agents.documentation_agent import DocumentationAgent
from regulaite.core.models import Asset, RiskReport

kernel  = Kernel(); process = Process(kernel)
disc    = DiscoveryAgent(); policy = PolicyAgent(); doc = DocumentationAgent()

@kernel.tool(name="discover_assets")
def _discover(_:str): return [a.dict() for a in disc.discover()]

@kernel.tool(name="classify_risk")
def _classify(asset_json:str):
    asset=Asset.parse_raw(asset_json)
    return policy.analyse(asset).json()

@kernel.tool(name="generate_pdf")
def _pdf(reports_json:str):
    reps=[RiskReport.parse_obj(r) for r in json.loads(reports_json)]
    return doc.generate(reps)

process.call_tool("discover_assets").foreach("asset") \
    .call_tool("classify_risk").end().call_tool("generate_pdf")

if __name__=="__main__":
    ap=argparse.ArgumentParser(); ap.add_argument("--repo",default="example/demo")
    args=ap.parse_args(); disc.repo=args.repo
    res=process.run(); print("PDF:", res.value)