"""
Tripletex AI Accounting Agent
Main FastAPI application
"""

import logging
from fastapi import FastAPI, Request, HTTPException, Header
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import sys

from config.settings import settings
from core.llm_service import LLMService
from core.file_processor import FileProcessor
from core.task_executor import TaskExecutor
from tripletex.client import TripletexClient

# Configure logging
import os

# Only use file logging in local development
handlers = [logging.StreamHandler(sys.stdout)]
if os.getenv('RAILWAY_ENVIRONMENT') is None:
    # Local development - add file logging
    try:
        handlers.append(logging.FileHandler('tripletex_agent.log'))
    except Exception:
        pass  # Ignore if file logging fails

logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=handlers
)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Tripletex AI Accounting Agent",
    description="AI agent for completing accounting tasks in Tripletex",
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

# Initialize services
llm_service = LLMService()
file_processor = FileProcessor()


# Request/Response Models
class FileAttachment(BaseModel):
    filename: str
    content_base64: str
    mime_type: str


class TripletexCredentials(BaseModel):
    base_url: str
    session_token: str


class SolveRequest(BaseModel):
    prompt: str
    files: Optional[List[FileAttachment]] = []
    tripletex_credentials: TripletexCredentials


class SolveResponse(BaseModel):
    status: str


@app.get("/")
async def root():
    """Root endpoint - health check"""
    return {
        "status": "ok",
        "service": "Tripletex AI Accounting Agent",
        "version": "1.0.0"
    }


@app.get("/health")
async def health():
    """Detailed health check"""
    return {
        "status": "healthy",
        "version": "1.0.0",
        "model": settings.OPENAI_MODEL
    }


@app.post("/solve", response_model=SolveResponse)
async def solve(
    request: SolveRequest,
    authorization: Optional[str] = Header(None)
):
    """
    Main endpoint for solving Tripletex accounting tasks
    
    Args:
        request: Task request with prompt, files, and credentials
        authorization: Optional Bearer token for API key authentication
    
    Returns:
        {"status": "completed"} on success
    """
    try:
        # Verify API key if configured
        if settings.API_KEY:
            if not authorization or not authorization.startswith("Bearer "):
                raise HTTPException(
                    status_code=401,
                    detail="Missing or invalid authorization header"
                )
            
            token = authorization.replace("Bearer ", "")
            if token != settings.API_KEY:
                raise HTTPException(status_code=401, detail="Invalid API key")
        
        logger.info(f"Received task: {request.prompt[:100]}...")
        
        # 1. Process files if any
        processed_files = []
        if request.files:
            logger.info(f"Processing {len(request.files)} files")
            processed_files = file_processor.process_files([
                {
                    "filename": f.filename,
                    "content_base64": f.content_base64,
                    "mime_type": f.mime_type
                }
                for f in request.files
            ])
            logger.info(f"Files processed: {[f.get('filename') for f in processed_files]}")
        
        # 2. Initialize Tripletex client
        tripletex_client = TripletexClient(
            base_url=request.tripletex_credentials.base_url,
            session_token=request.tripletex_credentials.session_token
        )
        
        # 3. Analyze prompt with LLM
        logger.info("Analyzing prompt with LLM")
        task_analysis = llm_service.analyze_prompt(request.prompt, processed_files)
        logger.info(
            f"Task analysis complete: {task_analysis.get('task_type')} "
            f"(language: {task_analysis.get('language')}, "
            f"confidence: {task_analysis.get('confidence', 0):.2f})"
        )
        
        # 4. Execute task
        logger.info("Executing task")
        executor = TaskExecutor(tripletex_client)
        result = executor.execute_task(task_analysis)
        
        # 5. Log results
        if result.get("status") == "success":
            stats = result.get("efficiency", {})
            logger.info(
                f"Task completed successfully - "
                f"API calls: {stats.get('total_calls', 0)}, "
                f"Errors: {stats.get('error_calls', 0)}, "
                f"Success rate: {stats.get('success_rate', 0):.2%}"
            )
        else:
            logger.error(f"Task failed: {result.get('error')}")
        
        # Return success response
        return SolveResponse(status="completed")
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


if __name__ == "__main__":
    import uvicorn
    
    logger.info(f"Starting Tripletex AI Agent on {settings.HOST}:{settings.PORT}")
    logger.info(f"Using OpenAI model: {settings.OPENAI_MODEL}")
    
    uvicorn.run(
        app,
        host=settings.HOST,
        port=settings.PORT,
        log_level=settings.LOG_LEVEL.lower()
    )

# Made with Bob
