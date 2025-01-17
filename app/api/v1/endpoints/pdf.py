from fastapi import APIRouter, HTTPException, Query, Depends, UploadFile, File
from fastapi.responses import Response, JSONResponse, HTMLResponse
from app.services.pdf_service import PDFService
from app.models.pdf_options import (
    PDFRequest, 
    PDFCompressionRequest, 
    CompressionLevel,
    PDFOptions,
    Margin,
    PageFormat
)
from app.core.security import get_api_key
import tempfile
import os
import markdown
from typing import Optional
from pydantic import BaseModel, Field

class MarkdownRequest(BaseModel):
    """Request model for markdown to HTML conversion"""
    content: str = Field(
        ...,
        description="The markdown content to convert to HTML",
        examples=["""# Title\n\n## Section 1\nContent for section 1"""]
    )
    title: Optional[str] = Field(
        None,
        description="Optional title for the document",
        examples=["My Document"]
    )
    header: Optional[str] = Field(
        None,
        description="Optional header HTML content",
        examples=['<div class="header">My Header</div>']
    )
    footer: Optional[str] = Field(
        None,
        description="Optional footer HTML content",
        examples=['<div class="footer">Page 1 of 1</div>']
    )
    add_table_of_contents: bool = Field(
        False,
        description="Whether to add a table of contents at the start of the document"
    )
    theme: Optional[str] = Field(
        "light",
        description="Color theme for the document",
        examples=["light", "dark"]
    )
    font_family: Optional[str] = Field(
        None,
        description="Main font family for the document",
        examples=["Arial, sans-serif", "Times New Roman, serif", "Roboto, sans-serif"]
    )
    font_size: Optional[str] = Field(
        None,
        description="Base font size for the document",
        examples=["12pt", "14px", "1em"]
    )
    heading_font_family: Optional[str] = Field(
        None,
        description="Font family for headings",
        examples=["Georgia, serif", "Helvetica, sans-serif"]
    )
    line_height: Optional[str] = Field(
        None,
        description="Line height for the document",
        examples=["1.6", "1.5", "2"]
    )
    margin_top: Optional[str] = Field(
        None,
        description="Top margin of the document",
        examples=["20px", "1in", "2cm"]
    )
    margin_right: Optional[str] = Field(
        None,
        description="Right margin of the document",
        examples=["20px", "1in", "2cm"]
    )
    margin_bottom: Optional[str] = Field(
        None,
        description="Bottom margin of the document",
        examples=["20px", "1in", "2cm"]
    )
    margin_left: Optional[str] = Field(
        None,
        description="Left margin of the document",
        examples=["20px", "1in", "2cm"]
    )
    content_width: Optional[str] = Field(
        None,
        description="Width of the content area",
        examples=["800px", "21cm", "8.5in"]
    )

def convert_markdown_to_html(
    markdown_content: str, 
    title: Optional[str] = None,
    header: Optional[str] = None,
    footer: Optional[str] = None,
    add_toc: bool = False,
    theme: str = "light",
    font_family: Optional[str] = None,
    font_size: Optional[str] = None,
    heading_font_family: Optional[str] = None,
    line_height: Optional[str] = None,
    margin_top: Optional[str] = None,
    margin_right: Optional[str] = None,
    margin_bottom: Optional[str] = None,
    margin_left: Optional[str] = None,
    content_width: Optional[str] = None
) -> str:
    """Helper function to convert markdown to styled HTML"""
    # Convert Markdown to HTML with extended features
    extensions = [
        'extra',             # Tables, footnotes, attribute lists, etc.
        'codehilite',        # Code highlighting
        'fenced_code',       # Fenced code blocks
        'nl2br',             # Newlines to <br>
        'sane_lists',        # Better list handling
        'smarty',            # Smart quotes, dashes, etc.
        'tables',            # Tables
    ]
    
    if add_toc:
        extensions.append('toc')
        markdown_content = '[TOC]\n\n' + markdown_content

    html_content = markdown.markdown(
        markdown_content,
        extensions=extensions,
        output_format='html5'
    )

    # Process TRUE and FALSE to add color classes
    html_content = html_content.replace('>TRUE<', ' class="true">TRUE<')
    html_content = html_content.replace('>FALSE<', ' class="false">FALSE<')

    # Get theme colors
    colors = {
        "light": {
            "bg": "#ffffff",
            "text": "#333333",
            "border": "#e2e8f0",
            "heading": "#2d3748",
            "link": "#3182ce",
            "hover": "#2c5282",
            "code_bg": "#f7fafc",
            "blockquote": "#718096",
            "section_bg": "#f8fafc"
        },
        "dark": {
            "bg": "#1a202c",
            "text": "#e2e8f0",
            "border": "#4a5568",
            "heading": "#f7fafc",
            "link": "#63b3ed",
            "hover": "#90cdf4",
            "code_bg": "#2d3748",
            "blockquote": "#a0aec0",
            "section_bg": "#2d3748"
        }
    }[theme]

    # Default settings
    default_font_family = "-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif"
    default_heading_font = default_font_family
    default_font_size = "12pt"
    default_line_height = "1.6"
    default_margin = "20px"
    default_content_width = "800px"

    # Create a complete HTML document with styling
    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <title>{title or 'Markdown Document'}</title>
        <style>
            :root {{
                color-scheme: {theme};
            }}
            body {{
                font-family: {font_family or default_font_family};
                line-height: {line_height or default_line_height};
                font-size: {font_size or default_font_size};
                color: {colors["text"]};
                background-color: {colors["bg"]};
                /* Remove fixed margins to allow PDF options to control them */
                margin: {margin_top or default_margin} {margin_right or default_margin} {margin_bottom or default_margin} {margin_left or default_margin};
                padding: 0;
            }}
            .container {{
                width: 100%;
                /* Remove fixed margins */
                padding: 0;
            }}
            .header {{
                position: sticky;
                top: 0;
                background-color: {colors["bg"]};
                border-bottom: 1px solid {colors["border"]};
                padding: 1rem 0;
                margin-bottom: 2rem;
                z-index: 100;
                width: 100%;
            }}
            .footer {{
                margin-top: 2rem;
                padding: 1rem 0;
                border-top: 1px solid {colors["border"]};
                text-align: center;
                font-size: 0.875rem;
                color: {colors["blockquote"]};
                width: 100%;
            }}
            .markdown-content {{
                /* Allow content width to be controlled while keeping it centered */
                width: {content_width or default_content_width};
                margin: 0 auto;
                background-color: {colors["bg"]};
                padding: 0;
            }}
            h1, h2, h3, h4, h5, h6 {{
                font-family: {heading_font_family or font_family or default_heading_font};
                font-weight: 600;
                line-height: 1.25;
                margin-top: 1.5em;
                margin-bottom: 0.5em;
                color: {colors["heading"]};
            }}
            h1 {{ font-size: 2em; margin-top: 0; }}
            h2 {{ font-size: 1.5em; }}
            h3 {{ font-size: 1.25em; }}
            h4 {{ font-size: 1em; }}
            h5 {{ font-size: 0.875em; }}
            h6 {{ font-size: 0.85em; }}
            p {{
                margin: 1em 0;
            }}
            ul, ol {{
                margin: 1em 0;
                padding-left: 2em;
            }}
            li + li {{
                margin-top: 0.25em;
            }}
            li > p {{
                margin: 0.5em 0;
            }}
            blockquote {{
                margin: 1em 0;
                padding: 0.5em 1em;
                color: {colors["blockquote"]};
                border-left: 4px solid {colors["border"]};
                background-color: {colors["section_bg"]};
            }}
            code {{
                font-family: 'SFMono-Regular', Consolas, 'Liberation Mono', Menlo, Courier, monospace;
                padding: 0.2em 0.4em;
                margin: 0;
                font-size: 85%;
                background-color: {colors["code_bg"]};
                border-radius: 3px;
            }}
            pre {{
                font-family: 'SFMono-Regular', Consolas, 'Liberation Mono', Menlo, Courier, monospace;
                padding: 1em;
                overflow: auto;
                font-size: 85%;
                line-height: 1.45;
                background-color: {colors["code_bg"]};
                border-radius: 6px;
                margin: 1em 0;
            }}
            pre code {{
                padding: 0;
                margin: 0;
                font-size: 100%;
                background-color: transparent;
            }}
            table {{
                width: 100%;
                border-collapse: collapse;
                margin: 1em 0;
                overflow-x: auto;
                display: block;
            }}
            table th, table td {{
                padding: 0.5em 1em;
                border: 1px solid {colors["border"]};
            }}
            table tr:nth-child(2n) {{
                background-color: {colors["section_bg"]};
            }}
            img {{
                max-width: 100%;
                height: auto;
                border-radius: 6px;
            }}
            hr {{
                height: 1px;
                border: none;
                background-color: {colors["border"]};
                margin: 2em 0;
            }}
            strong {{
                color: {colors["heading"]};
                font-weight: 600;
            }}
            .true {{
                color: #48bb78;
                font-weight: bold;
            }}
            .false {{
                color: #f56565;
                font-weight: bold;
            }}
            .experience-section {{
                background-color: {colors["section_bg"]};
                border: 1px solid {colors["border"]};
                border-radius: 8px;
                padding: 1.5em;
                margin: 1.5em 0;
            }}
            .experience-header {{
                display: flex;
                justify-content: space-between;
                align-items: flex-start;
                margin-bottom: 1em;
            }}
            .experience-title {{
                margin: 0;
                color: {colors["heading"]};
            }}
            .experience-meta {{
                color: {colors["blockquote"]};
                font-size: 0.875em;
            }}
            .experience-content {{
                margin-top: 1em;
            }}
            .toc {{
                background-color: {colors["section_bg"]};
                padding: 1.5em;
                border-radius: 8px;
                margin: 1.5em 0;
            }}
            .toc ul {{
                list-style-type: none;
                padding-left: 1em;
            }}
            .toc a {{
                color: {colors["link"]};
                text-decoration: none;
            }}
            .toc a:hover {{
                color: {colors["hover"]};
                text-decoration: underline;
            }}
            @media print {{
                body {{
                    /* Reset all margins for PDF generation */
                    margin: 0 !important;
                    padding: 0 !important;
                    background-color: transparent !important;
                }}
                .container {{
                    margin: 0 !important;
                    padding: 0 !important;
                    width: 100% !important;
                }}
                .markdown-content {{
                    /* Reset content constraints for PDF */
                    width: 100% !important;
                    max-width: none !important;
                    margin: 0 !important;
                    padding: 0 !important;
                    background-color: transparent !important;
                }}
                .header, .footer {{
                    display: none !important;
                }}
                h1:first-of-type {{
                    margin-top: 0 !important;
                    padding-top: 0 !important;
                }}
                /* Hide default headers and footers */
                title, head {{
                    display: none !important;
                }}
            }}
        </style>
    </head>
    <body>
        {f'<div class="header">{header}</div>' if header else ''}
        <div class="container">
            <div class="markdown-content">
                {html_content}
            </div>
        </div>
        {f'<div class="footer">{footer}</div>' if footer else ''}
    </body>
    </html>
    """

router = APIRouter()
pdf_service = PDFService()

@router.post("/markdown-to-html")
async def markdown_to_html(
    request: MarkdownRequest,
    api_key: str = Depends(get_api_key)
) -> HTMLResponse:
    """
    Convert Markdown content to styled HTML.
    
    The request body should be a JSON object with the following structure:
    ```json
    {
        "content": "# Your Markdown Content\n\n## Section 1\nContent here...",
        "title": "Optional Document Title",
        "header": "<div>Optional Header HTML</div>",
        "footer": "<div>Optional Footer HTML</div>",
        "add_table_of_contents": false,
        "theme": "light"
    }
    ```
    
    Returns an HTML response with proper styling for markdown elements.
    
    Requires a valid API key in the x-api-key header.
    """
    try:
        html_content = convert_markdown_to_html(
            request.content,
            title=request.title,
            header=request.header,
            footer=request.footer,
            add_toc=request.add_table_of_contents,
            theme=request.theme,
            font_family=request.font_family,
            font_size=request.font_size,
            heading_font_family=request.heading_font_family,
            line_height=request.line_height,
            margin_top=request.margin_top,
            margin_right=request.margin_right,
            margin_bottom=request.margin_bottom,
            margin_left=request.margin_left,
            content_width=request.content_width
        )
        return HTMLResponse(content=html_content)
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Markdown to HTML conversion failed: {str(e)}"
        )

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