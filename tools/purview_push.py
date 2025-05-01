import os, json, uuid
from azure.identity import DefaultAzureCredential
from azure.purview.catalog import PurviewCatalogClient
from regulaite.orchestrator import Orchestrator

PURVIEW = os.getenv("PURVIEW_NAME")
client  = PurviewCatalogClient(f"https://{PURVIEW}.purview.azure.com",
                               credential=DefaultAzureCredential())

def push():
    result = Orchestrator().run()
    entities=[]
    for r in result["reports"]:
        entities.append({
          "id"   : str(uuid.uuid4()),
          "type" : "microsoft.regulaite_risk",
          "name" : r["asset_id"],
          "properties": r
        })
    client.dataplane.add_or_update_entities({"entities":entities})

if __name__=="__main__": push()