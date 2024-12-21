import os
import tempfile
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager

class PDFService:
    def __init__(self):
        self.setup_chrome_options()
        
    def setup_chrome_options(self):
        self.chrome_options = Options()
        self.chrome_options.add_argument('--headless')
        self.chrome_options.add_argument('--no-sandbox')
        self.chrome_options.add_argument('--disable-dev-shm-usage')
        self.chrome_options.add_argument('--disable-gpu')
        # Set paper size to A4
        self.chrome_options.add_argument('--print-to-pdf-no-header')
        self.chrome_options.add_argument('--print-to-pdf')

    def generate_pdf(self, html_content: str) -> bytes:
        # Create a temporary HTML file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.html', delete=False) as f:
            f.write(html_content)
            temp_html = f.name

        # Create a temporary PDF file
        temp_pdf = tempfile.mktemp(suffix='.pdf')

        try:
            # Initialize Chrome driver
            driver = webdriver.Chrome(
                service=Service(ChromeDriverManager().install()),
                options=self.chrome_options
            )

            # Load HTML content
            driver.get(f'file:///{temp_html}')

            # Print page to PDF
            print_options = {
                'printBackground': True,
                'paperWidth': 8.27,  # A4 width in inches
                'paperHeight': 11.69,  # A4 height in inches
                'marginTop': 0,
                'marginBottom': 0,
                'marginLeft': 0,
                'marginRight': 0
            }
            driver.execute_cdp_cmd('Page.printToPDF', print_options)

            # Read the generated PDF
            with open(temp_pdf, 'rb') as f:
                pdf_content = f.read()

            return pdf_content

        finally:
            # Clean up temporary files
            if os.path.exists(temp_html):
                os.unlink(temp_html)
            if os.path.exists(temp_pdf):
                os.unlink(temp_pdf)
            driver.quit() 