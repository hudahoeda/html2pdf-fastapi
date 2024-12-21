from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import Response, JSONResponse
from app.services.pdf_service import PDFService
from app.models.pdf_options import PDFRequest

router = APIRouter()
pdf_service = PDFService()

@router.post("/generate-pdf")
async def generate_pdf(
    request: PDFRequest,
    return_base64: bool = Query(
        False,
        description="If true, returns the PDF as a base64 string in JSON response"
    )
):
    """
    Generate a PDF from HTML content or URL with various options.
    
    The endpoint accepts a comprehensive set of options including:
    - HTML content or URL to render
    - Page format and size
    - Margins and orientation
    - Headers and footers
    - Custom scripts and styles
    - Authentication
    - Cookies
    - And more
    
    Returns either a PDF file or base64 encoded PDF string based on return_base64 parameter.
    """
    try:
        pdf_content = pdf_service.generate_pdf(request)
        
        if return_base64:
            import base64
            return JSONResponse(
                content={
                    "success": True,
                    "data": base64.b64encode(pdf_content).decode('utf-8')
                }
            )
        
        return Response(
            content=pdf_content,
            media_type="application/pdf",
            headers={
                "Content-Disposition": "attachment; filename=generated.pdf"
            }
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"PDF generation failed: {str(e)}"
        ) 