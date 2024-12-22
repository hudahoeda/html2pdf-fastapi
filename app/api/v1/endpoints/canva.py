from typing import Dict, Union

from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse, JSONResponse
from pydantic import BaseModel

from app.services.canva_service import CanvaService

router = APIRouter()
canva_service = CanvaService()

class CanvaRequest(BaseModel):
    html_content: str
    cert_name: str
    as_zip: bool = False

@router.post("/canva2html", response_model=None)
async def convert_canva_to_html(request: CanvaRequest) -> Union[JSONResponse, StreamingResponse]:
    """
    Convert Canva HTML to clean HTML with downloaded assets.
    
    Parameters:
    - html_content: The HTML content from Canva's embed code
    - cert_name: A unique name for the certificate (used for file naming)
    - as_zip: If true, returns a ZIP file containing all generated files. If false, returns file paths (default: false)
    
    Returns:
    - If as_zip is false: JSON response containing paths to the generated HTML and CSS files
    - If as_zip is true: ZIP file containing all generated files
    """
    try:
        result = await canva_service.convert_canva_html(
            html_content=request.html_content,
            cert_name=request.cert_name,
            as_zip=request.as_zip
        )
        
        if isinstance(result, StreamingResponse):
            return result
        
        return JSONResponse(content=result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) 