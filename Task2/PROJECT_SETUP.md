# Task 2: Project Setup Guide

## Project Structure

```
Task2/
├── main.py                          # FastAPI app entry point
├── requirements.txt                 # Python dependencies
├── .env.example                     # Environment variables template
├── .env                            # Local environment (gitignored)
├── Dockerfile                       # Container configuration
├── .gitignore                      # Git ignore rules
├── README.md                        # Project documentation
│
├── config/
│   ├── __init__.py
│   ├── settings.py                 # Configuration management
│   └── task_definitions.py         # Task type definitions and mappings
│
├── api/
│   ├── __init__.py
│   ├── endpoints.py                # /solve endpoint implementation
│   └── models.py                   # Pydantic request/response models
│
├── core/
│   ├── __init__.py
│   ├── prompt_parser.py            # LLM-based prompt analysis
│   ├── language_detector.py        # Language identification
│   ├── file_processor.py           # PDF/image handling
│   └── task_router.py              # Route tasks to handlers
│
├── tripletex/
│   ├── __init__.py
│   ├── client.py                   # API client with authentication
│   ├── endpoints.py                # Endpoint wrappers
│   └── models.py                   # Tripletex data models
│
├── handlers/
│   ├── __init__.py
│   ├── base.py                     # Base handler class
│   │
│   ├── tier1/
│   │   ├── __init__.py
│   │   ├── employee.py             # Employee operations
│   │   ├── customer.py             # Customer operations
│   │   └── product.py              # Product operations
│   │
│   ├── tier2/
│   │   ├── __init__.py
│   │   ├── invoice.py              # Invoice operations
│   │   ├── payment.py              # Payment operations
│   │   ├── project.py              # Project operations
│   │   └── travel_expense.py       # Travel expense operations
│   │
│   └── tier3/
│       ├── __init__.py
│       ├── reconciliation.py       # Bank reconciliation
│       └── corrections.py          # Error corrections
│
├── utils/
│   ├── __init__.py
│   ├── logger.py                   # Logging configuration
│   ├── efficiency_tracker.py      # API call tracking
│   └── validators.py               # Data validation helpers
│
├── tests/
│   ├── __init__.py
│   ├── test_handlers.py            # Handler unit tests
│   ├── test_api_client.py          # API client tests
│   ├── test_prompt_parser.py       # Prompt parsing tests
│   └── test_integration.py         # End-to-end tests
│
└── scripts/
    ├── test_local.py               # Local testing script
    ├── deploy.sh                   # Deployment script
    └── sandbox_test.py             # Sandbox testing script
```

## requirements.txt

```txt
# Web Framework
fastapi==0.109.0
uvicorn[standard]==0.27.0
pydantic==2.5.3
pydantic-settings==2.1.0

# HTTP Client
requests==2.31.0
httpx==0.26.0

# LLM Integration
openai==1.10.0
anthropic==0.18.0
langchain==0.1.6
langchain-openai==0.0.5

# File Processing
PyPDF2==3.0.1
pdfplumber==0.10.3
Pillow==10.2.0
pytesseract==0.3.10

# Utilities
python-dotenv==1.0.0
loguru==0.7.2
tenacity==8.2.3
python-multipart==0.0.6

# Development
pytest==7.4.4
pytest-asyncio==0.23.3
black==24.1.1
flake8==7.0.0
mypy==1.8.0

# Deployment
gunicorn==21.2.0
```

## .env.example

```env
# LLM Configuration
OPENAI_API_KEY=sk-your-openai-key-here
# OR
ANTHROPIC_API_KEY=sk-ant-your-anthropic-key-here

# LLM Model Selection
LLM_PROVIDER=openai  # or anthropic
LLM_MODEL=gpt-4-turbo-preview  # or claude-3-opus-20240229

# Tripletex Sandbox (for local testing)
SANDBOX_BASE_URL=https://kkpqfuj-amager.tripletex.dev/v2
SANDBOX_SESSION_TOKEN=your_sandbox_token_here

# Server Configuration
HOST=0.0.0.0
PORT=8000
LOG_LEVEL=INFO
WORKERS=4

# Optional: API Key for endpoint protection
API_KEY=your_secret_api_key_here

# Optional: Monitoring
SENTRY_DSN=your_sentry_dsn_here
```

## .gitignore

```gitignore
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg

# Virtual Environment
venv/
env/
ENV/

# Environment Variables
.env
.env.local

# IDE
.vscode/
.idea/
*.swp
*.swo
*~

# Logs
*.log
logs/

# Testing
.pytest_cache/
.coverage
htmlcov/

# Temporary Files
/tmp/
*.tmp

# macOS
.DS_Store

# Deployment
.railway/
.render/
```

## Dockerfile

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    tesseract-ocr \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Expose port
EXPOSE 8000

# Run application
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

## main.py (Skeleton)

```python
"""
Tripletex AI Accounting Agent
Main FastAPI application entry point
"""

from fastapi import FastAPI, Request, HTTPException, Header
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import base64
import logging
from pathlib import Path
import os

from config.settings import settings
from core.prompt_parser import PromptParser
from core.task_router import TaskRouter
from tripletex.client import TripletexClient
from utils.logger import setup_logging

# Setup logging
setup_logging()
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Tripletex AI Agent",
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

# Initialize components
prompt_parser = PromptParser()
task_router = TaskRouter()

@app.get("/")
async def root():
    """Health check endpoint"""
    return {"status": "ok", "service": "Tripletex AI Agent"}

@app.get("/health")
async def health():
    """Detailed health check"""
    return {
        "status": "healthy",
        "version": "1.0.0",
        "llm_provider": settings.LLM_PROVIDER
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
                raise HTTPException(status_code=401, detail="Missing or invalid authorization")
            
            token = authorization.replace("Bearer ", "")
            if token != settings.API_KEY:
                raise HTTPException(status_code=401, detail="Invalid API key")
        
        logger.info(f"Received task: {request.prompt[:100]}...")
        
        # 1. Process files if any
        processed_files = []
        for file in request.files:
            file_data = base64.b64decode(file.content_base64)
            file_path = Path(f"/tmp/{file.filename}")
            file_path.write_bytes(file_data)
            processed_files.append({
                "filename": file.filename,
                "path": str(file_path),
                "mime_type": file.mime_type
            })
            logger.info(f"Processed file: {file.filename}")
        
        # 2. Initialize Tripletex client
        api_client = TripletexClient(
            base_url=request.tripletex_credentials.base_url,
            session_token=request.tripletex_credentials.session_token
        )
        
        # 3. Analyze prompt with LLM
        task_analysis = prompt_parser.analyze(request.prompt, processed_files)
        logger.info(f"Task type: {task_analysis['task_type']}, Language: {task_analysis.get('language', 'unknown')}")
        
        # 4. Route to appropriate handler and execute
        result = task_router.execute(task_analysis, api_client)
        
        # 5. Log efficiency stats
        stats = api_client.get_efficiency_stats()
        logger.info(
            f"Task completed - API calls: {stats['total_calls']}, "
            f"Errors: {stats['error_calls']}, "
            f"Success rate: {stats['success_rate']:.2%}"
        )
        
        return SolveResponse(status="completed")
        
    except Exception as e:
        logger.error(f"Task failed: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        app,
        host=settings.HOST,
        port=settings.PORT,
        log_level=settings.LOG_LEVEL.lower()
    )
```

## config/settings.py

```python
"""
Configuration management using pydantic-settings
"""

from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    """Application settings"""
    
    # LLM Configuration
    OPENAI_API_KEY: Optional[str] = None
    ANTHROPIC_API_KEY: Optional[str] = None
    LLM_PROVIDER: str = "openai"  # or "anthropic"
    LLM_MODEL: str = "gpt-4-turbo-preview"
    
    # Tripletex Sandbox
    SANDBOX_BASE_URL: Optional[str] = None
    SANDBOX_SESSION_TOKEN: Optional[str] = None
    
    # Server Configuration
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    LOG_LEVEL: str = "INFO"
    WORKERS: int = 4
    
    # Security
    API_KEY: Optional[str] = None
    
    # Monitoring
    SENTRY_DSN: Optional[str] = None
    
    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()
```

## utils/logger.py

```python
"""
Logging configuration using loguru
"""

import sys
from loguru import logger
from pathlib import Path

def setup_logging():
    """Configure logging for the application"""
    
    # Remove default handler
    logger.remove()
    
    # Add console handler with custom format
    logger.add(
        sys.stdout,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan> - <level>{message}</level>",
        level="INFO"
    )
    
    # Add file handler
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)
    
    logger.add(
        log_dir / "tripletex_agent.log",
        rotation="500 MB",
        retention="10 days",
        level="DEBUG",
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function} - {message}"
    )
    
    return logger
```

## Installation Steps

### 1. Create Project Structure

```bash
cd Task2

# Create all directories
mkdir -p config api core tripletex handlers/tier1 handlers/tier2 handlers/tier3 utils tests scripts

# Create __init__.py files
touch config/__init__.py
touch api/__init__.py
touch core/__init__.py
touch tripletex/__init__.py
touch handlers/__init__.py
touch handlers/tier1/__init__.py
touch handlers/tier2/__init__.py
touch handlers/tier3/__init__.py
touch utils/__init__.py
touch tests/__init__.py
```

### 2. Set Up Virtual Environment

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Environment

```bash
cp .env.example .env
# Edit .env with your actual credentials
```

### 5. Run Tests

```bash
pytest tests/
```

### 6. Start Development Server

```bash
uvicorn main:app --reload
```

## Next Steps

1. Implement core components (prompt parser, API client, handlers)
2. Test with sandbox account
3. Iterate and improve based on results
4. Deploy to production
5. Submit to competition

See [`IMPLEMENTATION_GUIDE.md`](./IMPLEMENTATION_GUIDE.md) for detailed implementation patterns.