from fastapi import APIRouter
from datetime import datetime
from core.config import METEOMATICS_USER, SMTP_HOST, SMTP_USER, SMTP_PASSWORD, SLM_PROVIDER, OLLAMA_MODEL
from core.database import db

router = APIRouter(prefix="/health", tags=["Health"])

@router.get("/")
async def health_check():
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "services": {
            "meteomatics": "ok" if METEOMATICS_USER else "not configured",
            "mongodb": "ok" if db else "not configured",
            "email": "ok" if SMTP_HOST and SMTP_USER and SMTP_PASSWORD else "not configured",
            "slm": {"provider": SLM_PROVIDER, "model": OLLAMA_MODEL}
        }
    }
