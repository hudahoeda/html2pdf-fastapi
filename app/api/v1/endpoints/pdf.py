from fastapi import APIRouter, HTTPException, Query, Depends, UploadFile, File
from fastapi.responses import Response, JSONResponse
from app.services.pdf_service import PDFService
from app.models.pdf_options import PDFRequest, PDFCompressionRequest, CompressionLevel
from app.core.security import get_api_key
import tempfile
import os

router = APIRouter()
pdf_service = PDFService()

@router.post("/generate-pdf")
async def generate_pdf(
    request: PDFRequest,
    api_key: str = Depends(get_api_key),
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
    
    Requires a valid API key in the x-api-key header.
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

@router.post("/compress-pdf")
async def compress_pdf(
    file: UploadFile = File(...),
    compression_level: CompressionLevel = Query(
        CompressionLevel.LEVEL_5,
        description="Compression level from 0 (no compression) to 9 (maximum compression)"
    ),
    api_key: str = Depends(get_api_key),
    return_base64: bool = Query(
        False,
        description="If true, returns the PDF as a base64 string in JSON response"
    )
):
    """
    Compress a PDF file with specified compression level.
    
    Parameters:
    - file: PDF file to compress
    - compression_level: Integer from 1 (minimum compression) to 5 (maximum compression)
    - return_base64: If true, returns base64 encoded string instead of file
    
    Returns either a compressed PDF file or base64 encoded PDF string.
    
    Requires a valid API key in the x-api-key header.
    """
    if not file.filename.lower().endswith('.pdf'):
        raise HTTPException(
            status_code=400,
            detail="Uploaded file must be a PDF"
        )
    
    try:
        # Save uploaded file temporarily
        with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp_file:
            content = await file.read()
            tmp_file.write(content)
            tmp_file.flush()
            
            # Compress the PDF
            compressed_content = pdf_service.compress_pdf(
                tmp_file.name,
                compression_level.value
            )
            
            # Clean up
            os.unlink(tmp_file.name)
            
            if return_base64:
                import base64
                return JSONResponse(
                    content={
                        "success": True,
                        "data": base64.b64encode(compressed_content).decode('utf-8')
                    }
                )
            
            return Response(
                content=compressed_content,
                media_type="application/pdf",
                headers={
                    "Content-Disposition": f"attachment; filename=compressed_{file.filename}"
                }
            )
            
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"PDF compression failed: {str(e)}"
        ) 