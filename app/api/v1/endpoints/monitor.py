from fastapi import APIRouter, Request, Depends, HTTPException, Form, Response, status
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from app.core.celery_app import celery_app
from datetime import datetime
from app.core.config import settings

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")

def verify_session(request: Request):
    """Verify session has valid API key"""
    api_key = request.session.get("api_key")
    if not api_key or api_key != settings.API_KEY:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or missing API key"
        )
    return api_key

@router.get("/", response_class=HTMLResponse)
async def monitor_page(request: Request):
    # Check if user is logged in
    if request.session.get("api_key") != settings.API_KEY:
        return templates.TemplateResponse("login.html", {
            "request": request,
            "error": request.query_params.get("error")
        })
    return templates.TemplateResponse("monitor.html", {"request": request})

@router.post("/login")
async def login(
    request: Request,
    response: Response,
    api_key: str = Form(...)
):
    if api_key == settings.API_KEY:
        request.session["api_key"] = api_key
        return RedirectResponse(
            url="/api/v1/monitor/",
            status_code=status.HTTP_302_FOUND
        )
    return templates.TemplateResponse(
        "login.html",
        {
            "request": request,
            "error": "Invalid API key"
        },
        status_code=status.HTTP_401_UNAUTHORIZED
    )

@router.get("/logout")
async def logout(request: Request):
    request.session.clear()
    return RedirectResponse(
        url="/api/v1/monitor/",
        status_code=status.HTTP_302_FOUND
    )

@router.get("/stats/{stat_type}")
async def get_stats(
    stat_type: str,
    request: Request,
    _: str = Depends(verify_session)
):
    i = celery_app.control.inspect()
    active = i.active() or {}
    reserved = i.reserved() or {}
    revoked = i.revoked() or {}
    
    # Get stats from Redis
    stats = {
        "total": len(celery_app.backend.client.keys("celery-task-meta-*")),
        "pending": sum(len(tasks) for tasks in active.values()) + sum(len(tasks) for tasks in reserved.values()),
        "completed": len([k for k in celery_app.backend.client.keys("celery-task-meta-*") 
                         if celery_app.backend.get(k).get("status") == "SUCCESS"]),
        "failed": len([k for k in celery_app.backend.client.keys("celery-task-meta-*") 
                      if celery_app.backend.get(k).get("status") == "FAILURE"])
    }
    
    return str(stats.get(stat_type, 0))

@router.get("/jobs")
async def get_jobs(
    request: Request,
    _: str = Depends(verify_session)
):
    # Get all task keys
    task_keys = celery_app.backend.client.keys("celery-task-meta-*")
    jobs = []
    
    for key in task_keys[-50:]:  # Get last 50 jobs
        result = celery_app.backend.get(key)
        if result:
            task_id = key.decode().replace("celery-task-meta-", "")
            status = result.get("status")
            created_at = datetime.fromtimestamp(result.get("date_done")).strftime("%Y-%m-%d %H:%M:%S")
            
            # Calculate duration
            if status == "SUCCESS":
                start_time = result.get("date_start")
                end_time = result.get("date_done")
                duration = f"{end_time - start_time:.2f}s" if start_time and end_time else "-"
            else:
                duration = "-"
            
            jobs.append({
                "id": task_id,
                "status": status,
                "created_at": created_at,
                "duration": duration
            })
    
    # Sort by created_at descending
    jobs.sort(key=lambda x: x["created_at"], reverse=True)
    
    # Return HTML for the table rows
    rows_html = ""
    for job in jobs:
        status_class = {
            "SUCCESS": "text-green-500",
            "FAILURE": "text-red-500",
            "PENDING": "text-yellow-500",
            "STARTED": "text-blue-500"
        }.get(job["status"], "text-gray-500")
        
        rows_html += f"""
        <tr>
            <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">{job["id"]}</td>
            <td class="px-6 py-4 whitespace-nowrap text-sm {status_class} font-semibold">{job["status"]}</td>
            <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{job["created_at"]}</td>
            <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{job["duration"]}</td>
            <td class="px-6 py-4 whitespace-nowrap text-sm">
                <button 
                    hx-get="/api/v1/monitor/job/{job["id"]}"
                    hx-target="#job-details"
                    onclick="document.getElementById('job-modal').classList.remove('hidden')"
                    class="text-indigo-600 hover:text-indigo-900">
                    View Details
                </button>
            </td>
        </tr>
        """
    
    return HTMLResponse(rows_html)

@router.get("/job/{job_id}")
async def get_job_details(
    job_id: str,
    request: Request,
    _: str = Depends(verify_session)
):
    result = celery_app.backend.get(f"celery-task-meta-{job_id}")
    if not result:
        return HTMLResponse("<p>Job not found</p>")
    
    status = result.get("status")
    created_at = datetime.fromtimestamp(result.get("date_done")).strftime("%Y-%m-%d %H:%M:%S")
    traceback = result.get("traceback")
    
    details_html = f"""
    <div class="space-y-4">
        <div>
            <h4 class="font-medium text-gray-700">Status</h4>
            <p class="mt-1">{status}</p>
        </div>
        <div>
            <h4 class="font-medium text-gray-700">Created At</h4>
            <p class="mt-1">{created_at}</p>
        </div>
    """
    
    if traceback:
        details_html += f"""
        <div>
            <h4 class="font-medium text-gray-700">Error Details</h4>
            <pre class="mt-1 bg-red-50 p-4 rounded text-sm overflow-x-auto">{traceback}</pre>
        </div>
        """
    
    details_html += "</div>"
    return HTMLResponse(details_html) 