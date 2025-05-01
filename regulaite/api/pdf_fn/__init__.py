import logging
import os
import azure.functions as func

def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Processing PDF download request')
    
    try:
        # Get PDF name from route parameter
        pdf_name = req.route_params.get('name')
        if not pdf_name:
            return func.HttpResponse(
                "PDF name not provided",
                status_code=400
            )
        
        # Construct path to PDF file
        pdf_path = os.path.join(os.path.dirname(__file__), '..', pdf_name)
        
        # Check if file exists
        if not os.path.exists(pdf_path):
            return func.HttpResponse(
                f"PDF {pdf_name} not found",
                status_code=404
            )
        
        # Read PDF file
        with open(pdf_path, 'rb') as f:
            pdf_data = f.read()
        
        # Return PDF with correct content type
        return func.HttpResponse(
            pdf_data,
            mimetype='application/pdf',
            headers={
                'Content-Disposition': f'attachment; filename="{pdf_name}"',
                'Access-Control-Allow-Origin': '*'
            }
        )
        
    except Exception as e:
        logging.error(f'Error serving PDF: {str(e)}')
        return func.HttpResponse(
            "Internal server error",
            status_code=500
        )