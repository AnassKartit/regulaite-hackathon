from regulaite.orchestrator import Orchestrator
def test_pipeline(): assert "assets" in Orchestrator().run()