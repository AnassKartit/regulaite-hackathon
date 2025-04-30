import logging
import json
import azure.functions as func

app = func.FunctionApp()

@app.function_name(name="upload-law")
@app.route(route="upload-law", auth_level=func.AuthLevel.ANONYMOUS, methods=["POST", "OPTIONS"])
def http_trigger(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Processing law upload request')
    
    # Handle CORS preflight
    if req.method == "OPTIONS":
        return func.HttpResponse(
            status_code=200,
            headers={
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Methods": "POST",
                "Access-Control-Allow-Headers": "Content-Type"
            }
        )

    try:
        files = req.files
        if not files or 'file' not in files:
            raise ValueError("No file uploaded")

        file = files['file']
        if not file.filename.endswith('.pdf'):
            raise ValueError("Only PDF files are supported")

        # TODO: Implement file processing logic here
        
        return func.HttpResponse(
            json.dumps({"message": "File uploaded successfully"}),
            mimetype="application/json",
            headers={
                "Access-Control-Allow-Origin": "*",
                "Content-Type": "application/json"
            }
        )
    except Exception as e:
        logging.error(f'Error in upload function: {str(e)}', exc_info=True)
        return func.HttpResponse(
            json.dumps({"error": str(e)}),
            status_code=400,
            mimetype="application/json",
            headers={
                "Access-Control-Allow-Origin": "*",
                "Content-Type": "application/json"
            }
        )