from fastapi import APIRouter, HTTPException
from datetime import datetime
from models.schemas import EmailSubscription
from core.database import db
import logging

router = APIRouter(prefix="/subscriptions", tags=["Subscriptions"])
logger = logging.getLogger("air-api")

@router.post("/subscribe")
async def subscribe_email(subscription: EmailSubscription):
    """
    Inscreve um usuário para alertas de qualidade do ar via e-mail.
    Armazena os dados no MongoDB.
    """
    if db is None:
        raise HTTPException(status_code=503, detail="MongoDB não configurado")

    try:
        thresholds = subscription.thresholds or {}
        if not isinstance(thresholds, dict):
            raise HTTPException(status_code=400, detail="'thresholds' deve ser um objeto")

        data = {
            "email": subscription.email,
            "location": subscription.location,
            "profile": subscription.profile,
            "thresholds": thresholds,
            "subscribed_at": datetime.utcnow(),
            "active": True
        }
        result = db["subscriptions"].insert_one(data)
        logger.info("✅ Nova inscrição salva para %s", subscription.email)
        return {"success": True, "subscription_id": str(result.inserted_id)}

    except Exception as e:
        logger.exception("Erro ao salvar inscrição: %s", e)
        raise HTTPException(status_code=500, detail=f"Erro ao salvar inscrição: {e}")

@router.get("/")
async def list_subscriptions(limit: int = 100):
    """
    Lista as inscrições ativas armazenadas no banco de dados.
    """
    if db is None:
        raise HTTPException(status_code=503, detail="MongoDB não configurado")

    try:
        cursor = db["subscriptions"].find({"active": True}).limit(limit)
        subscriptions = []
        for sub in cursor:
            sub["_id"] = str(sub["_id"])
            subscriptions.append(sub)
        return {"success": True, "total": len(subscriptions), "subscriptions": subscriptions}

    except Exception as e:
        logger.exception("Erro ao listar inscrições: %s", e)
        raise HTTPException(status_code=500, detail=f"Erro ao listar inscrições: {e}")
