import os, requests, re
from typing import List
from ..core.models import Asset

PAT = os.getenv("GITHUB_PAT")
API = "https://api.github.com/graphql"
HEAD = {"Authorization": f"Bearer {PAT}"} if PAT else {}

QL = lambda repo: {
    "query": f"""
    {{
      search(query: "repo:{repo} (openai|face)", type: CODE, first: 50) {{
        nodes {{ ... on Code {{ path url }} }}
      }}
    }}
    """
}

def discover_github_assets(repo:str)->List[Asset]:
    if not PAT:
        return []
    r = requests.post(API, json=QL(repo), headers=HEAD, timeout=30)
    r.raise_for_status()
    nodes = r.json()["data"]["search"]["nodes"]
    return [
        Asset(asset_id=os.path.basename(n["path"]),
              type="model",
              location="github",
              code_ref=n["url"])
        for n in nodes if re.search(r"\.(py|cs|js|java)$", n["path"])
    ]
