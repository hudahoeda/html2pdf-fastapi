from io import BytesIO
import json
from pathlib import Path
from typing import Dict, List, Optional, Union
import zipfile

import cairosvg
import requests
from bs4 import BeautifulSoup
from PIL import Image
from fastapi import HTTPException
from fastapi.responses import StreamingResponse


class CanvaService:
    def __init__(self):
        self.static_dir = Path("static/canva")
        self.static_dir.mkdir(parents=True, exist_ok=True)

    async def convert_canva_html(self, html_content: str, cert_name: str, as_zip: bool = False) -> Union[Dict[str, str], StreamingResponse]:
        """Convert Canva HTML to clean HTML with downloaded assets."""
        try:
            soup = BeautifulSoup(html_content, "html.parser")
            
            # Create directory for this certificate
            cert_dir = self.static_dir / cert_name
            cert_dir.mkdir(exist_ok=True)
            
            # Process CSS
            all_css = await self._process_css(soup)
            css_path = cert_dir / f"style-{cert_name}.css"
            
            # Clean up HTML
            self._clean_html(soup)
            
            # Process fonts and add to CSS
            all_css = await self._process_fonts(soup, all_css)
            
            # Save CSS
            css_path.write_text(all_css)
            
            # Process images
            await self._process_images(soup, cert_dir)
            
            # Create final HTML
            final_html = self._create_final_html(soup, cert_name)
            html_path = cert_dir / f"canva-{cert_name}.html"
            html_path.write_text(final_html)

            if as_zip:
                return await self._create_zip_response(cert_dir, cert_name)
            
            return {
                "html_path": str(html_path.relative_to(self.static_dir)),
                "css_path": str(css_path.relative_to(self.static_dir)),
                "message": "Successfully converted Canva HTML"
            }
            
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error converting Canva HTML: {str(e)}")

    async def _create_zip_response(self, cert_dir: Path, cert_name: str) -> StreamingResponse:
        """Create a ZIP file containing all generated files."""
        zip_buffer = BytesIO()
        
        with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zip_file:
            # Add all files from the certificate directory
            for file_path in cert_dir.rglob("*"):
                if file_path.is_file():
                    # Use relative path within the ZIP
                    arc_name = file_path.relative_to(cert_dir)
                    zip_file.write(file_path, arc_name)
        
        # Seek to the beginning of the buffer
        zip_buffer.seek(0)
        
        # Return streaming response
        return StreamingResponse(
            zip_buffer,
            media_type="application/zip",
            headers={
                "Content-Disposition": f'attachment; filename="{cert_name}.zip"'
            }
        )

    async def _process_css(self, soup: BeautifulSoup) -> str:
        """Extract and combine all CSS from the HTML."""
        all_css = ""
        for tag in soup.find_all("link", rel="stylesheet"):
            css_url = tag["href"]
            try:
                response = requests.get(css_url)
                if response.ok:
                    all_css += response.text
            except Exception as e:
                print(f"Failed to fetch CSS from {css_url}: {e}")
        return all_css

    def _clean_html(self, soup: BeautifulSoup) -> None:
        """Remove unnecessary elements from HTML."""
        # Remove navigation
        nav = soup.find("div", {"role": "navigation"})
        if nav:
            nav.decompose()
        
        # Remove other unnecessary elements
        for tag in ["button", "a", "script"]:
            for element in soup.find_all(tag):
                element.decompose()

    async def _process_fonts(self, soup: BeautifulSoup, css: str) -> str:
        """Extract and process fonts from the HTML."""
        for script in soup.find_all("script"):
            if "window['bootstrap']" in script.text:
                try:
                    json_content = script.text.split("'")[7]
                    fonts_data = json.loads(json_content)["page"]["Bj"]["A"]["H"]
                    css += self._generate_font_faces(fonts_data)
                except Exception as e:
                    print(f"Error processing fonts: {e}")
        return css

    def _generate_font_faces(self, fonts_data: List[Dict]) -> str:
        """Generate @font-face CSS rules."""
        font_css = ""
        for font in fonts_data:
            name = f'{font["A"]} {font["B"]}'
            for style in font.get("D", []):
                font_css += self._create_font_face(name, style)
        return font_css

    def _create_font_face(self, name: str, style: Dict) -> str:
        """Create a single @font-face CSS rule."""
        style_name = style.get("style", "")
        font_style = {
            "BOLD": "font-weight: 700",
            "ITALICS": "font-style: italic",
            "REGULAR": "font-weight: 400; font-style: normal",
            "BOLD_ITALICS": "font-weight: 700; font-style: italic"
        }.get(style_name, "font-weight: 400")
        
        sources = []
        for file_data in style.get("files", []):
            if url := file_data.get("url"):
                format_type = file_data.get("format", "").lower().replace("otf", "opentype").replace("ttf", "truetype")
                sources.append(f'url({url}) format("{format_type}")')
        
        if sources:
            return f'\n@font-face {{font-family: "{name}"; {font_style}; src: {", ".join(sources)}}}'
        return ""

    async def _process_images(self, soup: BeautifulSoup, cert_dir: Path) -> None:
        """Download and process images."""
        for num, img in enumerate(soup.find_all("img")):
            image_url = img["src"]
            ext = image_url.split(".")[-1].split("?")[0]
            
            new_name = f"image-{num}.{'png' if ext == 'svg' else ext}"
            img["src"] = new_name
            
            try:
                if ext == "svg":
                    await self._process_svg_image(image_url, cert_dir / new_name)
                else:
                    await self._process_regular_image(image_url, cert_dir / new_name)
            except Exception as e:
                print(f"Error processing image {image_url}: {e}")

    async def _process_svg_image(self, url: str, save_path: Path) -> None:
        """Process SVG images by converting them to PNG."""
        out = BytesIO()
        cairosvg.svg2png(url=url, write_to=out)
        img = Image.open(out)
        img.save(save_path, quality=90)

    async def _process_regular_image(self, url: str, save_path: Path) -> None:
        """Process regular images by downloading and saving them."""
        response = requests.get(url, stream=True)
        if response.ok:
            img = Image.open(response.raw)
            img.save(save_path, quality=90)

    def _create_final_html(self, soup: BeautifulSoup, cert_name: str) -> str:
        """Create the final HTML with proper head and meta tags."""
        head = f"""
        <meta charset="utf-8">
        <title>Certificate - {cert_name}</title>
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <meta name="author" content="Generated via Canva"/>
        <link href="style-{cert_name}.css" rel="stylesheet">
        <style>@page {{ size: A4 landscape; margin: 0; }}</style>"""
        
        return f"""<html dir="ltr" lang="en">
        <head>{head}</head>
        {soup.body.prettify()}
        </html>""" 