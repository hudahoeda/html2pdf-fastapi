# HTML to PDF FastAPI Service

A FastAPI-based service that converts HTML content to PDF using Selenium and Chrome headless browser.

## Features

- Convert HTML to PDF using Chrome's high-fidelity rendering
- RESTful API endpoint for PDF generation
- Configurable page settings (A4 format, margins, etc.)
- CORS support for cross-origin requests
- Error handling and proper cleanup of temporary files

## Prerequisites

- Python 3.9+
- Google Chrome browser installed
- pip (Python package manager)

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/html2pdf-fastapi.git
cd html2pdf-fastapi
```

2. Install the required dependencies:
```bash
pip install -r requirements.txt
```

## Running the Service

Start the FastAPI server:
```bash
uvicorn app.main:app --reload
```

The service will be available at:
- API Documentation: http://localhost:8000/docs
- Base URL: http://localhost:8000

## API Usage

### Generate PDF

**Endpoint:** `POST /api/v1/generate-pdf`

**Request Body:**
```json
{
    "html_content": "<html><body><h1>Hello World</h1></body></html>"
}
```

**Response:**
- Content-Type: application/pdf
- The response will be a PDF file download

### Example using cURL

```bash
curl -X POST "http://localhost:8000/api/v1/generate-pdf" \
     -H "Content-Type: application/json" \
     -d '{"html_content": "<html><body><h1>Hello World</h1></body></html>"}' \
     --output output.pdf
```

### Example using Python requests

```python
import requests

url = "http://localhost:8000/api/v1/generate-pdf"
html_content = "<html><body><h1>Hello World</h1></body></html>"

response = requests.post(
    url,
    json={"html_content": html_content}
)

if response.status_code == 200:
    with open("output.pdf", "wb") as f:
        f.write(response.content)
```

## Error Handling

The service returns appropriate HTTP status codes:
- 200: Successful PDF generation
- 400: Invalid request (e.g., missing or invalid HTML content)
- 500: Server error (e.g., PDF generation failure)

## Development

The project structure follows FastAPI best practices:
```
html2pdf-fastapi/
├── app/
│   ├── api/
│   │   └── v1/
│   │       └── endpoints/
│   │           └── pdf.py
│   ├── services/
│   │   └── pdf_service.py
│   └── main.py
├── requirements.txt
└── README.md
```

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details. 