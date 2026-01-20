"""
AIReady File Converter
FastAPI application for converting human documents to AI-ready formats.
"""

import os
import uuid
import shutil
import asyncio
from pathlib import Path
from datetime import datetime, timezone, timedelta
from typing import Optional
from contextlib import asynccontextmanager
import zipfile
from io import BytesIO

# #region agent log
import json as _json
import os as _os
_LOG_PATH = _os.environ.get("DEBUG_LOG_PATH", "/tmp/ai_ready_debug.log")
_DEBUG_ENABLED = _os.environ.get("DEBUG_LOGGING", "false").lower() == "true"
def _dbg(loc, msg, data, hyp):
    if not _DEBUG_ENABLED:
        return
    try:
        with open(_LOG_PATH, "a") as f:
            f.write(_json.dumps({"location": loc, "message": msg, "data": data, "hypothesisId": hyp, "timestamp": datetime.now().isoformat(), "sessionId": "debug-session"}) + "\n")
    except Exception:
        pass  # Silently ignore logging failures in production
# #endregion

from fastapi import FastAPI, File, UploadFile, HTTPException, Request, Response
from fastapi.responses import FileResponse, StreamingResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from converters import (
    get_converter,
    get_default_format,
    get_supported_extensions,
)

# Configuration
UPLOAD_DIR = Path("/tmp/ai_ready_file_converter")
MAX_TOTAL_SIZE = 10 * 1024 * 1024  # 10MB total limit
SESSION_TIMEOUT_MINUTES = 15

# Ensure upload directory exists
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

# Track active sessions
sessions: dict[str, dict] = {}


async def cleanup_expired_sessions():
    """Background task to clean up expired sessions."""
    while True:
        await asyncio.sleep(60)  # Check every minute
        now = datetime.now(timezone.utc)
        expired = []
        
        for session_id, session_data in sessions.items():
            last_activity = session_data.get("last_activity", now)
            if now - last_activity > timedelta(minutes=SESSION_TIMEOUT_MINUTES):
                expired.append(session_id)
        
        for session_id in expired:
            session_dir = UPLOAD_DIR / session_id
            if session_dir.exists():
                shutil.rmtree(session_dir, ignore_errors=True)
            sessions.pop(session_id, None)
            print(f"Cleaned up expired session: {session_id}")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application lifespan."""
    # Start background cleanup task
    cleanup_task = asyncio.create_task(cleanup_expired_sessions())
    yield
    # Cleanup on shutdown
    cleanup_task.cancel()
    try:
        await cleanup_task
    except asyncio.CancelledError:
        pass


app = FastAPI(
    title="AIReady File Converter",
    description="Convert human documents to AI-ready formats",
    version="1.0.0",
    lifespan=lifespan
)

# Mount static files
static_path = Path(__file__).parent / "static"
static_path.mkdir(parents=True, exist_ok=True)
app.mount("/static", StaticFiles(directory=static_path), name="static")

# Templates
templates_path = Path(__file__).parent / "templates"
templates_path.mkdir(parents=True, exist_ok=True)
templates = Jinja2Templates(directory=templates_path)


def get_or_create_session(request: Request) -> str:
    """Get existing session or create a new one."""
    session_id = request.cookies.get("session_id")
    
    if not session_id or session_id not in sessions:
        session_id = str(uuid.uuid4())
        sessions[session_id] = {
            "files": {},
            "converted": {},
            "last_activity": datetime.now(timezone.utc),
            "total_size": 0
        }
        # Create session directory
        session_dir = UPLOAD_DIR / session_id
        session_dir.mkdir(parents=True, exist_ok=True)
        (session_dir / "uploads").mkdir(exist_ok=True)
        (session_dir / "converted").mkdir(exist_ok=True)
    else:
        sessions[session_id]["last_activity"] = datetime.now(timezone.utc)
    
    return session_id


def get_session_dir(session_id: str) -> Path:
    """Get the session directory path."""
    return UPLOAD_DIR / session_id


@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    """Serve the main page."""
    return templates.TemplateResponse("index.html", {"request": request})


@app.get("/api/session")
async def get_session(request: Request, response: Response):
    """Get or create a session."""
    session_id = get_or_create_session(request)
    response.set_cookie(
        key="session_id",
        value=session_id,
        httponly=True,
        samesite="strict",
        max_age=SESSION_TIMEOUT_MINUTES * 60
    )
    return {
        "session_id": session_id,
        "files": list(sessions[session_id]["files"].values()),
        "supported_extensions": get_supported_extensions()
    }


@app.post("/api/upload")
async def upload_file(
    request: Request,
    response: Response,
    file: UploadFile = File(...)
):
    """Upload a file for conversion."""
    session_id = get_or_create_session(request)
    response.set_cookie(
        key="session_id",
        value=session_id,
        httponly=True,
        samesite="strict",
        max_age=SESSION_TIMEOUT_MINUTES * 60
    )
    
    session = sessions[session_id]
    
    # Validate file extension
    filename = file.filename or "unknown"
    ext = Path(filename).suffix.lower()
    
    if not get_converter(ext):
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file type: {ext}. Supported: {', '.join(get_supported_extensions())}"
        )
    
    # Read file content
    content = await file.read()
    file_size = len(content)
    
    # Validate total size limit
    if session["total_size"] + file_size > MAX_TOTAL_SIZE:
        raise HTTPException(
            status_code=400,
            detail=f"Total upload size would exceed {MAX_TOTAL_SIZE // (1024*1024)}MB limit. Please remove some files first."
        )
    
    # Generate unique file ID
    file_id = str(uuid.uuid4())[:8]
    
    # Save file
    session_dir = get_session_dir(session_id)
    upload_path = session_dir / "uploads" / f"{file_id}_{filename}"
    
    with open(upload_path, "wb") as f:
        f.write(content)
    
    # Get default output format
    default_format = get_default_format(ext)
    
    # Store file info in session
    file_info = {
        "id": file_id,
        "filename": filename,
        "extension": ext,
        "size": file_size,
        "upload_path": str(upload_path),
        "output_format": default_format,
        "status": "uploaded",
        "converted_path": None
    }
    
    session["files"][file_id] = file_info
    session["total_size"] += file_size
    session["last_activity"] = datetime.now(timezone.utc)
    
    return {
        "success": True,
        "file": file_info
    }


@app.post("/api/set-format/{file_id}")
async def set_output_format(
    request: Request,
    file_id: str,
    format: str
):
    """Set the output format for a file."""
    session_id = request.cookies.get("session_id")
    
    if not session_id or session_id not in sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    
    session = sessions[session_id]
    
    if file_id not in session["files"]:
        raise HTTPException(status_code=404, detail="File not found")
    
    if format not in ("md", "json"):
        raise HTTPException(status_code=400, detail="Format must be 'md' or 'json'")
    
    session["files"][file_id]["output_format"] = format
    session["last_activity"] = datetime.now(timezone.utc)
    
    return {"success": True, "format": format}


@app.post("/api/convert")
async def convert_files(request: Request):
    """Convert all uploaded files."""
    session_id = request.cookies.get("session_id")
    
    if not session_id or session_id not in sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    
    session = sessions[session_id]
    session_dir = get_session_dir(session_id)
    
    results = []
    
    for file_id, file_info in session["files"].items():
        if file_info["status"] == "converted":
            # Already converted
            results.append({
                "id": file_id,
                "filename": file_info["filename"],
                "status": "already_converted",
                "output_filename": file_info.get("output_filename")
            })
            continue
        
        try:
            # #region agent log
            _dbg("main.py:290", "Starting conversion", {"file_id": file_id, "filename": file_info["filename"], "extension": file_info["extension"]}, "A")
            # #endregion
            
            # Get converter
            converter_class = get_converter(file_info["extension"])
            if not converter_class:
                raise ValueError(f"No converter for {file_info['extension']}")
            
            # Convert file
            upload_path = Path(file_info["upload_path"])
            # #region agent log
            _dbg("main.py:302", "Upload path check", {"path": str(upload_path), "exists": upload_path.exists()}, "A")
            # #endregion
            converter = converter_class(upload_path)
            
            output_format = file_info["output_format"]
            # #region agent log
            _dbg("main.py:308", "Calling get_output", {"output_format": output_format}, "A")
            # #endregion
            output_content = converter.get_output(output_format)
            # #region agent log
            _dbg("main.py:312", "get_output completed", {"output_length": len(output_content) if output_content else 0}, "C")
            # #endregion
            output_filename = converter.get_output_filename(output_format)
            
            # Save converted file
            converted_path = session_dir / "converted" / f"{file_id}_{output_filename}"
            with open(converted_path, "w", encoding="utf-8") as f:
                f.write(output_content)
            
            # Update file info
            file_info["status"] = "converted"
            file_info["converted_path"] = str(converted_path)
            file_info["output_filename"] = output_filename
            file_info["converted_at"] = datetime.now(timezone.utc).isoformat()
            
            # #region agent log
            _dbg("main.py:328", "Conversion SUCCESS", {"file_id": file_id, "output_filename": output_filename}, "A")
            # #endregion
            
            results.append({
                "id": file_id,
                "filename": file_info["filename"],
                "status": "converted",
                "output_filename": output_filename,
                "output_format": output_format,
                "converted_at": file_info["converted_at"]
            })
            
        except Exception as e:
            # #region agent log
            import traceback
            _dbg("main.py:343", "Conversion FAILED", {"file_id": file_id, "error": str(e), "error_type": type(e).__name__, "traceback": traceback.format_exc()}, "A")
            # #endregion
            file_info["status"] = "error"
            file_info["error"] = str(e)
            results.append({
                "id": file_id,
                "filename": file_info["filename"],
                "status": "error",
                "error": str(e)
            })
    
    session["last_activity"] = datetime.now(timezone.utc)
    
    return {
        "success": True,
        "results": results
    }


@app.get("/api/download/{file_id}")
async def download_file(request: Request, file_id: str):
    """Download a converted file."""
    session_id = request.cookies.get("session_id")
    
    if not session_id or session_id not in sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    
    session = sessions[session_id]
    
    if file_id not in session["files"]:
        raise HTTPException(status_code=404, detail="File not found")
    
    file_info = session["files"][file_id]
    
    if file_info["status"] != "converted":
        raise HTTPException(status_code=400, detail="File not yet converted")
    
    converted_path = Path(file_info["converted_path"])
    
    if not converted_path.exists():
        raise HTTPException(status_code=404, detail="Converted file not found")
    
    session["last_activity"] = datetime.now(timezone.utc)
    
    return FileResponse(
        path=converted_path,
        filename=file_info["output_filename"],
        media_type="application/octet-stream"
    )


@app.get("/api/preview/{file_id}")
async def preview_file(request: Request, file_id: str):
    """Get a preview of the converted file content."""
    session_id = request.cookies.get("session_id")
    
    if not session_id or session_id not in sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    
    session = sessions[session_id]
    
    if file_id not in session["files"]:
        raise HTTPException(status_code=404, detail="File not found")
    
    file_info = session["files"][file_id]
    
    if file_info["status"] != "converted":
        raise HTTPException(status_code=400, detail="File not yet converted")
    
    converted_path = Path(file_info["converted_path"])
    
    if not converted_path.exists():
        raise HTTPException(status_code=404, detail="Converted file not found")
    
    with open(converted_path, "r", encoding="utf-8") as f:
        content = f.read()
    
    # Return preview (first 2000 chars)
    preview = content[:2000]
    if len(content) > 2000:
        preview += "\n\n... [truncated]"
    
    return {
        "filename": file_info["output_filename"],
        "format": file_info["output_format"],
        "preview": preview,
        "full_size": len(content)
    }


@app.get("/api/download-all")
async def download_all(request: Request):
    """Download all converted files as a ZIP bundle."""
    session_id = request.cookies.get("session_id")
    
    if not session_id or session_id not in sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    
    session = sessions[session_id]
    
    # Check if there are any converted files
    converted_files = [
        f for f in session["files"].values()
        if f["status"] == "converted"
    ]
    
    if not converted_files:
        raise HTTPException(status_code=400, detail="No converted files to download")
    
    # Create ZIP in memory
    zip_buffer = BytesIO()
    
    with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zip_file:
        for file_info in converted_files:
            converted_path = Path(file_info["converted_path"])
            if converted_path.exists():
                zip_file.write(converted_path, file_info["output_filename"])
    
    zip_buffer.seek(0)
    
    session["last_activity"] = datetime.now(timezone.utc)
    
    return StreamingResponse(
        zip_buffer,
        media_type="application/zip",
        headers={
            "Content-Disposition": "attachment; filename=converted_files.zip"
        }
    )


@app.delete("/api/file/{file_id}")
async def delete_file(request: Request, file_id: str):
    """Remove a file from the session."""
    session_id = request.cookies.get("session_id")
    
    if not session_id or session_id not in sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    
    session = sessions[session_id]
    
    if file_id not in session["files"]:
        raise HTTPException(status_code=404, detail="File not found")
    
    file_info = session["files"][file_id]
    
    # Delete uploaded file
    upload_path = Path(file_info["upload_path"])
    if upload_path.exists():
        upload_path.unlink()
    
    # Delete converted file if exists
    if file_info.get("converted_path"):
        converted_path = Path(file_info["converted_path"])
        if converted_path.exists():
            converted_path.unlink()
    
    # Update session
    session["total_size"] -= file_info["size"]
    del session["files"][file_id]
    session["last_activity"] = datetime.now(timezone.utc)
    
    return {"success": True}


@app.delete("/api/clear")
async def clear_session(request: Request):
    """Clear all files from the session."""
    session_id = request.cookies.get("session_id")
    
    if not session_id or session_id not in sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    
    session_dir = get_session_dir(session_id)
    
    # Delete all files
    if session_dir.exists():
        shutil.rmtree(session_dir, ignore_errors=True)
        session_dir.mkdir(parents=True, exist_ok=True)
        (session_dir / "uploads").mkdir(exist_ok=True)
        (session_dir / "converted").mkdir(exist_ok=True)
    
    # Reset session
    sessions[session_id] = {
        "files": {},
        "converted": {},
        "last_activity": datetime.now(timezone.utc),
        "total_size": 0
    }
    
    return {"success": True}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
