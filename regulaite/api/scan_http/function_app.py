import logging
import json
import os
import azure.functions as func
from regulaite.orchestrator import Orchestrator

app = func.FunctionApp()

@app.function_name(name="scan")
@app.route(route="scan", auth_level="anonymous", methods=["POST", "OPTIONS"])
def scan(req: func.HttpRequest) -> func.HttpResponse:
    """
    HTTP trigger function for scanning repositories.
    """
    logging.info('Processing scan request')
    
    # Handle CORS preflight
    if req.method.lower() == "options":
        return func.HttpResponse(
            status_code=200,
            headers={
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Methods": "POST, OPTIONS",
                "Access-Control-Allow-Headers": "Content-Type"
            }
        )
    
    try:
        # Get repo from request body or use default
        req_body = req.get_json() if req.get_body() else {}
        repo = req_body.get("repo") or os.getenv("GITHUB_REPO", "example/demo")
        logging.info(f'Scanning repo: {repo}')
        
        # Run orchestrator
        orchestrator = Orchestrator(repo)
        result = orchestrator.run()
        
        return func.HttpResponse(
            json.dumps(result),
            mimetype="application/json",
            headers={
                "Access-Control-Allow-Origin": "*",
                "Content-Type": "application/json"
            }
        )
    except Exception as e:
        logging.error(f'Error in scan function: {str(e)}', exc_info=True)
        return func.HttpResponse(
            json.dumps({"error": str(e)}),
            status_code=500,
            mimetype="application/json",
            headers={
                "Access-Control-Allow-Origin": "*",
                "Content-Type": "application/json"
            }
        )