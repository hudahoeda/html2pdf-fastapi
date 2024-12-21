# HTML to PDF FastAPI Service

A FastAPI-based service that converts HTML content to PDF using Selenium and Chrome headless browser. This service provides high-fidelity PDF generation with support for modern web features, custom styling, and various output options.

## Features

- Convert HTML to PDF using Chrome's high-fidelity rendering
- RESTful API endpoint for PDF generation
- Configurable page settings (A4, Letter, etc.)
- Custom margins and orientation
- Headers and footers support
- API key authentication
- CORS support
- Docker support for easy deployment
- Comprehensive error handling
- Poetry for dependency management

## Prerequisites

- Docker and Docker Compose (recommended)
- Or:
  - Python 3.9+
  - Google Chrome browser
  - Poetry (Python package manager)

## Quick Start with Docker

1. Clone the repository:
```bash
git clone https://github.com/yourusername/html2pdf-fastapi.git
cd html2pdf-fastapi
```

2. Create a `.env` file with your API keys:
```bash
cp .env.example .env
# Edit .env with your actual API keys
```

3. Build and run with Docker Compose:
```bash
docker-compose up -d
```

The service will be available at http://localhost:8000.

## Manual Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/html2pdf-fastapi.git
cd html2pdf-fastapi
```

2. Install Poetry (if not already installed):
```bash
curl -sSL https://install.python-poetry.org | python3 -
```

3. Install dependencies:
```bash
poetry install
```

4. Configure API keys:
```bash
cp .env.example .env
# Edit .env with your actual API keys
```

5. Run the application:
```bash
poetry run uvicorn app.main:app --reload
```

## Development Setup

1. Install development dependencies:
```bash
poetry install --with dev
```

2. Set up pre-commit hooks:
```bash
poetry run pre-commit install
```

3. Format code:
```bash
poetry run black .
poetry run isort .
```

4. Run linting:
```bash
poetry run flake8
```

## API Usage

### Authentication

All API endpoints require an API key to be passed in the `x-api-key` header:

```bash
X-API-Key: your-api-key-here
```

### Generate PDF

**Endpoint:** `POST /api/v1/generate-pdf`

**Headers:**
```
Content-Type: application/json
X-API-Key: your-api-key-here
```

**Request Body:**
```json
{
    "html": "<html><body><h1>Hello World</h1></body></html>",
    "options": {
        "format": "A4",
        "landscape": true,
        "margin": {
            "top": "1in",
            "right": "1in",
            "bottom": "1in",
            "left": "1in"
        },
        "printBackground": true
    }
}
```

**Example using Python:**
```python
import requests

url = "http://localhost:8000/api/v1/generate-pdf"
headers = {
    "X-API-Key": "your-api-key-here",
    "Content-Type": "application/json"
}

payload = {
    "html": "<html><body><h1>Hello World</h1></body></html>",
    "options": {
        "format": "A4",
        "landscape": True
    }
}

response = requests.post(url, json=payload, headers=headers)

if response.status_code == 200:
    with open("output.pdf", "wb") as f:
        f.write(response.content)
```

**Example using cURL:**
```bash
curl -X POST "http://localhost:8000/api/v1/generate-pdf" \
     -H "X-API-Key: your-api-key-here" \
     -H "Content-Type: application/json" \
     -d '{"html":"<html><body><h1>Hello World</h1></body></html>"}' \
     --output output.pdf
```

## Configuration Options

### PDF Options

- `format`: Page format (A0-A5, Letter, Legal, Tabloid)
- `width`, `height`: Custom page dimensions
- `landscape`: Boolean for landscape orientation
- `margin`: Page margins (top, right, bottom, left)
- `scale`: Scale factor (0.1 to 2.0)
- `printBackground`: Include background graphics
- `displayHeaderFooter`: Show header and footer
- `headerTemplate`: HTML template for header
- `footerTemplate`: HTML template for footer
- `pageRanges`: Page ranges to print

### Additional Options

- `addScriptTag`: Add custom JavaScript
- `addStyleTag`: Add custom CSS
- `viewport`: Custom viewport settings
- `waitForTimeout`: Wait time after page load

### Environment Configuration

#### Service Configuration
The service can be configured using environment variables in your `.env` file:

```bash
# API Configuration
API_KEYS=["your-api-key-1","your-api-key-2"]
API_KEY_NAME=x-api-key

# Service Configuration
PORT=8000  # The port number for the FastAPI service
HOST=0.0.0.0  # The host address to bind to

# Timezone Configuration
TZ=UTC  # Your timezone (e.g., "America/New_York", "Europe/London", "Asia/Tokyo")
```

#### Port Configuration
The service port can be configured in two ways:

1. Using the `.env` file:
```bash
PORT=3000  # Change to your desired port
```

2. Using environment variables when starting Docker Compose:
```bash
PORT=3000 docker-compose up -d
```

#### Timezone Configuration
The timezone will be automatically detected from your system. However, you can override it in several ways:

1. Using the `.env` file:
```bash
TZ=America/New_York
```

2. Using environment variables:
```bash
TZ=Europe/London docker-compose up -d
```

3. System default (automatically detected)

Available timezones can be found in the [tz database](https://en.wikipedia.org/wiki/List_of_tz_database_time_zones).

## Development

### Project Structure
```
html2pdf-fastapi/
├── app/
│   ├── api/
│   │   └── v1/
│   │       └── endpoints/
│   │           └── pdf.py
│   ├── core/
│   │   ├── config.py
│   │   └── security.py
│   ├── models/
│   │   └── pdf_options.py
│   ├── services/
│   │   └── pdf_service.py
│   └── main.py
├── docker-compose.yml
├── Dockerfile
├── pyproject.toml
├── poetry.lock
└── README.md
```

### Running Tests
```bash
poetry run pytest
```

## Security Considerations

1. API Keys:
   - Store API keys securely
   - Rotate keys regularly
   - Use HTTPS in production

2. Input Validation:
   - All input is validated using Pydantic models
   - HTML content is rendered in a sandboxed environment

3. Resource Limits:
   - Configure appropriate timeouts
   - Set up rate limiting in production

## Production Deployment

1. Update API keys in `.env`
2. Configure appropriate security measures
3. Set up HTTPS
4. Configure logging
5. Set up monitoring

## Contributing

1. Fork the repository
2. Create your feature branch
3. Install development dependencies: `poetry install --with dev`
4. Make your changes
5. Run tests: `poetry run pytest`
6. Format code: `poetry run black . && poetry run isort .`
7. Create a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details. 