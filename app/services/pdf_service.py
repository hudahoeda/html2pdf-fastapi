import os
import tempfile
import logging
from pathlib import Path
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from selenium.common.exceptions import TimeoutException, WebDriverException

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class PDFService:
    def __init__(self):
        self.setup_chrome_options()
        
    def setup_chrome_options(self):
        self.chrome_options = Options()
        self.chrome_options.add_argument('--headless=new')  # Updated headless argument
        self.chrome_options.add_argument('--no-sandbox')
        self.chrome_options.add_argument('--disable-dev-shm-usage')
        self.chrome_options.add_argument('--disable-gpu')
        self.chrome_options.add_argument('--window-size=1280,1024')
        self.chrome_options.add_argument('--disable-software-rasterizer')
        self.chrome_options.add_experimental_option('excludeSwitches', ['enable-logging'])

    def generate_pdf(self, html_content: str) -> bytes:
        # Create a temporary directory to store files
        temp_dir = tempfile.mkdtemp()
        temp_html = Path(temp_dir) / "temp.html"
        temp_pdf = Path(temp_dir) / "output.pdf"
        driver = None

        try:
            # Write HTML content to file
            logger.info("Writing HTML content to temporary file")
            temp_html.write_text(html_content, encoding='utf-8')

            # Initialize Chrome driver
            logger.info("Initializing Chrome driver")
            service = Service(ChromeDriverManager().install())
            driver = webdriver.Chrome(
                service=service,
                options=self.chrome_options
            )

            # Load HTML content
            logger.info("Loading HTML content")
            driver.get(f'file:///{temp_html.absolute()}')

            # Wait for page to load completely
            try:
                WebDriverWait(driver, 10).until(
                    lambda d: d.execute_script('return document.readyState') == 'complete'
                )
            except TimeoutException:
                logger.warning("Page load timeout, attempting to continue...")

            # Print page to PDF
            logger.info("Generating PDF")
            print_options = {
                'printBackground': True,
                'paperWidth': 8.27,  # A4 width in inches
                'paperHeight': 11.69,  # A4 height in inches
                'marginTop': 0,
                'marginBottom': 0,
                'marginLeft': 0,
                'marginRight': 0,
                'scale': 1.0
            }
            
            pdf_data = driver.execute_cdp_cmd('Page.printToPDF', print_options)
            
            if not pdf_data or 'data' not in pdf_data:
                raise ValueError("Failed to generate PDF data")

            # Write PDF content
            import base64
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
                if temp_pdf.exists():
                    temp_pdf.unlink()
                os.rmdir(temp_dir)
            except Exception as e:
                logger.warning(f"Error while cleaning temporary files: {str(e)}") 