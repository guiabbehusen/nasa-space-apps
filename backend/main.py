from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import logging
from core.config import METEOMATICS_USER
from core.database import db
from routes import health, weather, air, subscriptions, alerts

app = FastAPI(
    title="Weather & Air Quality API - NASA Space Apps 2025",
    description="API para dados meteorológicos e qualidade do ar usando Meteomatics",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 🔗 Rotas
app.include_router(health.router)
app.include_router(weather.router)
app.include_router(air.router)
app.include_router(subscriptions.router)
app.include_router(alerts.router)

logger = logging.getLogger("air-api")

@app.on_event("startup")
async def startup_event():
    logger.info("\n" + "=" * 60)
    logger.info("🚀 Weather & Air Quality API - NASA Space Apps 2025")
    logger.info("=" * 60)
    logger.info("✅ FastAPI rodando")
    logger.info("%s Meteomatics: %s", "✅" if METEOMATICS_USER else "❌", "Configurado" if METEOMATICS_USER else "NÃO configurado")
    logger.info("%s MongoDB: %s", "✅" if db is not None else "⚠️ ", "Conectado" if db is not None else "NÃO configurado")
    logger.info("=" * 60)
    logger.info("📡 http://localhost:8000")
    logger.info("📖 Docs: http://localhost:8000/docs")
    logger.info("=" * 60 + "\n")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")
