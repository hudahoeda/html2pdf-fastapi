from fastapi import APIRouter, HTTPException
from fastapi.responses import Response
from pydantic import BaseModel
from app.services.pdf_service import PDFService

router = APIRouter()
pdf_service = PDFService()

class HTMLRequest(BaseModel):
    html_content: str

@router.post("/generate-pdf")
async def generate_pdf(request: HTMLRequest):
    try:
        pdf_content = pdf_service.generate_pdf(request.html_content)
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