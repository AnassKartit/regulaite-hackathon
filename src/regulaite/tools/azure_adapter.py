import os
from typing import List

from azure.identity import DefaultAzureCredential
from azure.mgmt.resourcegraph import ResourceGraphClient
from azure.mgmt.resourcegraph.models import QueryRequest

from ..core.models import Asset


def discover_azure_assets() -> List[Asset]:
    """
    Return a list of Cognitive Services accounts in the current subscription.
    Falls back to an empty list when credentials / network are unavailable
    (unit-test friendly).
    """
    cred = DefaultAzureCredential(exclude_interactive_browser_credential=False)
    sub_id = (
        os.getenv("AZ_SUBSCRIPTION_ID")
        or os.popen("az account show --query id -o tsv").read().strip()
    )
    client = ResourceGraphClient(cred)

    query = """
    Resources
    | where type =~ 'microsoft.cognitiveservices/accounts'
    | project id, name, kind, location, tags
    """

    try:
        rows = client.resources(QueryRequest(subscriptions=[sub_id], query=query)).data
    except Exception:  # offline / no permission (e.g. in CI)
        return []

    assets: List[Asset] = []
    for row in rows:
        tags = row.get("tags") or {}
        if not isinstance(tags, dict):
            tags = {}
        assets.append(
            Asset(
                asset_id=row["name"],
                type="service",
                location=row["location"],
                metadata=tags,
            )
        )
    return assets