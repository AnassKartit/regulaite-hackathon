import os
from typing import List
from ..core.models import Asset
from ..tools.azure_adapter  import discover_azure_assets
from ..tools.github_adapter import discover_github_assets

class DiscoveryAgent:
    def __init__(self, repo:str|None=None):
        self.repo = repo or os.getenv("GITHUB_REPO","example/demo")
    def discover(self)->List[Asset]:
        return discover_azure_assets() + discover_github_assets(self.repo)