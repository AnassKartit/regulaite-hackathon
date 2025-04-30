import pytest, json, os
from regulaite.agents.policy_agent import PolicyAgent
from regulaite.core.models import Asset

CASES = [
  ("public_surveillance", "Face", "unacceptable"),
  ("sector=credit", "model", "high"),
  ("chatbot", "service", "medium"),
]

@pytest.mark.parametrize("tag,kind,expect", CASES)
def test_static_map(tag, kind, expect):
    a = Asset(asset_id="x", type="service" if "Face" in kind else "model",
              location="swedencentral", metadata={"purpose": tag})
    level = PolicyAgent().analyse(a).risk_level
    assert level == expect