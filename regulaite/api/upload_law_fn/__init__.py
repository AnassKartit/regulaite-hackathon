import logging
import json
import azure.functions as func

def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Processing law upload request')
    
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
        if req.method.lower() == "options":
            return func.HttpResponse(
                status_code=200,
                headers={
                    "Access-Control-Allow-Origin": "*",
                    "Access-Control-Allow-Methods": "POST, OPTIONS",
                    "Access-Control-Allow-Headers": "Content-Type"
                }
            )

        # Verify content type
        content_type = req.headers.get('content-type', '').lower()
        if not content_type.startswith('multipart/form-data'):
            return func.HttpResponse(
                json.dumps({"error": "Content-Type must be multipart/form-data"}),
                status_code=415,  # Unsupported Media Type
                mimetype="application/json"
            )

        # Get file from form data
        files = req.files
        if not files or 'file' not in files:
            return func.HttpResponse(
                status_code=400,  # Bad Request
                body=json.dumps({"error": "No file uploaded"})
            )

        file = files['file']
        if not file.filename.endswith('.pdf'):
            return func.HttpResponse(
                status_code=415,  # Unsupported Media Type
                body=json.dumps({"error": "Only PDF files are supported"})
            )

        # Get the file content
        file_content = file.read()
        if not file_content:
            return func.HttpResponse(
                status_code=400,  # Bad Request
                body=json.dumps({"error": "File is empty"})
            )

        # Process the file
        # TODO: Implement actual file processing logic here
        logging.info(f"Processing file: {file.filename}, size: {len(file_content)} bytes")
        
        # Return success with no content if processing was successful
        return func.HttpResponse(
            status_code=204  # No Content
        )
    except Exception as e:
        logging.error(f'Error in upload function: {str(e)}', exc_info=True)
        return func.HttpResponse(
            status_code=500,  # Internal Server Error
            body=json.dumps({"error": "Internal server error occurred"})
        )