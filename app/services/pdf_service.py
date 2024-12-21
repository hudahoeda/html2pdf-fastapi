import os
import tempfile
import logging
import base64
from pathlib import Path
from typing import Optional, Union
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
from selenium.common.exceptions import TimeoutException, WebDriverException

from app.models.pdf_options import PDFRequest, PDFOptions, PageFormat

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class PDFService:
    def __init__(self):
        self.setup_chrome_options()
        
    def setup_chrome_options(self):
        self.chrome_options = Options()
        self.chrome_options.add_argument('--headless=new')
        self.chrome_options.add_argument('--no-sandbox')
        self.chrome_options.add_argument('--disable-dev-shm-usage')
        self.chrome_options.add_argument('--disable-gpu')
        self.chrome_options.add_argument('--disable-software-rasterizer')
        self.chrome_options.add_experimental_option('excludeSwitches', ['enable-logging'])

    def _convert_margin_to_inches(self, value: str) -> float:
        """Convert CSS-style margin values to inches"""
        if not value:
            return 0
        
        value = value.lower().strip()
        if value.endswith('px'):
            return float(value[:-2]) / 96  # Convert pixels to inches (96 DPI)
        elif value.endswith('in'):
            return float(value[:-2])
        elif value.endswith('cm'):
            return float(value[:-2]) / 2.54
        elif value.endswith('mm'):
            return float(value[:-2]) / 25.4
        elif value.endswith('pt'):
            return float(value[:-2]) / 72
        else:
            return float(value) / 96  # Assume pixels if no unit specified

    def _get_page_size(self, format: Optional[PageFormat], width: Optional[str], height: Optional[str]) -> dict:
        # Standard page sizes in inches
        page_sizes = {
            PageFormat.A0: {'width': 33.1, 'height': 46.8},
            PageFormat.A1: {'width': 23.4, 'height': 33.1},
            PageFormat.A2: {'width': 16.5, 'height': 23.4},
            PageFormat.A3: {'width': 11.7, 'height': 16.5},
            PageFormat.A4: {'width': 8.27, 'height': 11.69},
            PageFormat.A5: {'width': 5.83, 'height': 8.27},
            PageFormat.LETTER: {'width': 8.5, 'height': 11},
            PageFormat.LEGAL: {'width': 8.5, 'height': 14},
            PageFormat.TABLOID: {'width': 11, 'height': 17},
        }

        if width and height:
            return {
                'width': self._convert_margin_to_inches(width),
                'height': self._convert_margin_to_inches(height)
            }
        
        return page_sizes.get(format or PageFormat.A4)

    def generate_pdf(self, request: PDFRequest) -> Union[bytes, str]:
        temp_dir = tempfile.mkdtemp()
        temp_html = Path(temp_dir) / "temp.html"
        driver = None

        try:
            # Set viewport if specified
            if request.viewport:
                self.chrome_options.add_argument(
                    f'--window-size={request.viewport.width},{request.viewport.height}'
                )

            # Initialize Chrome driver
            logger.info("Initializing Chrome driver")
            service = Service(ChromeDriverManager().install())
            driver = webdriver.Chrome(service=service, options=self.chrome_options)

            # Load content
            logger.info("Writing HTML content to temporary file")
            temp_html.write_text(request.html or "", encoding='utf-8')
            driver.get(f'file:///{temp_html.absolute()}')

            # Wait for page load
            try:
                WebDriverWait(driver, request.options.timeout / 1000 if request.options else 10).until(
                    lambda d: d.execute_script('return document.readyState') == 'complete'
                )
            except TimeoutException:
                if not request.bestAttempt:
                    raise
                logger.warning("Page load timeout, attempting to continue...")

            # Generate PDF
            logger.info("Generating PDF")
            options = request.options or PDFOptions()
            page_size = self._get_page_size(options.format, options.width, options.height)
            
            print_options = {
                'scale': float(options.scale or 1.0),
                'printBackground': bool(options.printBackground),
                'paperWidth': float(page_size['width']),
                'paperHeight': float(page_size['height']),
                'marginTop': self._convert_margin_to_inches(options.margin.top) if options.margin else 0,
                'marginBottom': self._convert_margin_to_inches(options.margin.bottom) if options.margin else 0,
                'marginLeft': self._convert_margin_to_inches(options.margin.left) if options.margin else 0,
                'marginRight': self._convert_margin_to_inches(options.margin.right) if options.margin else 0,
                'landscape': bool(options.landscape),
                'preferCSSPageSize': bool(options.preferCSSPageSize)
            }

            # Add optional parameters only if they are specified and not None
            if options.displayHeaderFooter:
                print_options['displayHeaderFooter'] = True
                if options.headerTemplate:
                    print_options['headerTemplate'] = options.headerTemplate
                if options.footerTemplate:
                    print_options['footerTemplate'] = options.footerTemplate
            
            if options.pageRanges:
                print_options['pageRanges'] = options.pageRanges

            logger.info(f"Using print options: {print_options}")
            pdf_data = driver.execute_cdp_cmd('Page.printToPDF', print_options)
            
            if not pdf_data or 'data' not in pdf_data:
                raise ValueError("Failed to generate PDF data")

            pdf_content = base64.b64decode(pdf_data['data'])
            logger.info("PDF generation successful")
            
            return pdf_content

        except Exception as e:
            logger.error(f"PDF generation failed: {str(e)}", exc_info=True)
            raise

        finally:
            # Clean up resources
            logger.info("Cleaning up resources")
            if driver:
                try:
                    driver.quit()
                except Exception as e:
                    logger.warning(f"Error while closing driver: {str(e)}")

            # Clean up temporary files
            try:
                if temp_html.exists():
                    temp_html.unlink()
                os.rmdir(temp_dir)
            except Exception as e:
                logger.warning(f"Error while cleaning temporary files: {str(e)}") 