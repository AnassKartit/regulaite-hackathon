import os, pytest
from regulaite.core.models import Asset
from regulaite.agents.policy_agent import PolicyAgent

@pytest.mark.skipif(
    "AZURE_SEARCH_ENDPOINT" not in os.environ,
    reason="needs live Azure Search / OpenAI"
)
def test_live_rag():
    a = Asset(asset_id="live", type="model", location="sc", metadata={})
    rep = PolicyAgent().analyse(a)
    # we only assert the shape, not the exact model output
    assert rep.risk_level in {"unacceptable","high","medium","low"}