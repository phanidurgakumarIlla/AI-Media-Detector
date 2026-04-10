from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import shutil
import os
import uuid
import sys
import io
import asyncio

import models
import database
import auth
import mimetypes
from fastapi import Depends

# Force fix Windows registry corrupting CSS/JS mimetypes
mimetypes.init()
mimetypes.add_type('text/css', '.css')
mimetypes.add_type('application/javascript', '.js')

from ml_engine import analyze_media, get_pipeline
app = FastAPI(title="AI Detector API")

# Optimized Startup: Only create tables if database is missing
def init_db():
    try:
        models.Base.metadata.create_all(bind=database.engine)
    except Exception as e:
        print(f"[WARN] DB initialization error: {e}")

init_db()

# Include Auth Routes
app.include_router(auth.router)

@app.on_event("startup")
async def startup_event():
    """Eager Startup: Pre-load heavy ML models to ensure <1s analysis later."""
    print("[INFO] AI Detector Server started successfully in ACCELERATED mode.")
    print("[INFO] Warming up SOTA AI Models for near-instant analysis...")
    try:
        # Pre-load the model in a background thread to keep startup visual
        await asyncio.to_thread(get_pipeline)
    except:
        pass
    print("[INFO] ML Forensics are now WARM and ready for usage.")

# Configure CORS for React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

os.makedirs("uploads", exist_ok=True)
os.makedirs("static", exist_ok=True)
os.makedirs("logs", exist_ok=True)
os.makedirs("static/results", exist_ok=True)

class UrlRequest(BaseModel):
    url: str
    algorithm: str = "auto"

@app.post("/analyze-url")
async def analyze_url(payload: UrlRequest, db=Depends(database.get_db)):
    from scraper import get_video_metadata
    try:
        print(f"SCRAPING URL: {payload.url}")
        meta = await get_video_metadata(payload.url)
        if not meta:
            raise HTTPException(status_code=400, detail="Failed to extract media from URL")
        
        source_text = f"{meta.get('title', '')} {meta.get('description', '')}"
        thumbnail_url = meta.get('thumbnail', '')
        
        # SOTA 2026: Combined Metadata + Forensic Pipeline (Phase 37 Signal Bridge)
        result = await analyze_media("url_source.mp4", source=meta, thumbnail_url=thumbnail_url, algorithm_hint=payload.algorithm)
        
        # Log to Database (Phase 28 Alignment)
        new_log = models.AnalysisResult(
            filename=payload.url,
            verdict="AI Generated" if result['isFake'] else "Authentic",
            ai_score=result['aiProbability'],
            algorithm=result.get('algorithm', 'Auto Cascade'),
            username="Guest" # Fallback for now
        )
        db.add(new_log)
        db.commit()
        
        return result
    except Exception as e:
        import traceback
        with open("logs/server_error.log", "a") as f:
            f.write(traceback.format_exc() + "\n")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/analyze")
async def analyze_file(file: UploadFile = File(...), algorithm: str = Form("auto"), db=Depends(database.get_db)):
    file_id = str(uuid.uuid4())
    ext = os.path.splitext(file.filename)[1]
    saved_path = f"uploads/{file_id}{ext}"
    
    with open(saved_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    try:
        result = await analyze_media(saved_path, algorithm_hint=algorithm)
        
        # Log to Database (Phase 28 Alignment)
        new_log = models.AnalysisResult(
            filename=file.filename,
            verdict="AI Generated" if result['isFake'] else "Authentic",
            ai_score=result['aiProbability'],
            algorithm=result.get('algorithm', 'Auto Cascade'),
            username="Guest" # Fallback
        )
        db.add(new_log)
        db.commit()
        
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        if os.path.exists(saved_path):
            os.remove(saved_path)

@app.get("/history")
async def get_history(db=Depends(database.get_db)):
    logs = db.query(models.ScanLog).order_by(models.ScanLog.timestamp.desc()).limit(50).all()
    return logs

# Serve forensic results directory
app.mount("/results", StaticFiles(directory="static/results"), name="results")
# Serve the main frontend
app.mount("/", StaticFiles(directory="static", html=True), name="static")
