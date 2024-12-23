from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from app.api.v1.endpoints import pdf, monitor

app = FastAPI(
    title="HTML to PDF Service",
    description="A service to convert HTML to PDF using Selenium",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(pdf.router, prefix="/api/v1", tags=["pdf"])
app.include_router(monitor.router, prefix="/api/v1/monitor", tags=["monitor"])

@app.get("/")
async def root():
    return {"message": "HTML to PDF Service is running"} 