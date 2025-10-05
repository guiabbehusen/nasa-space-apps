from fastapi import APIRouter, HTTPException
from services.alerts import dispatch_alerts
import logging

router = APIRouter(prefix="/alerts", tags=["Alerts"])
logger = logging.getLogger("air-api")

@router.post("/dispatch")
async def trigger_alerts(lat: float, lon: float):
    """
    Dispara alertas de qualidade do ar para os assinantes via e-mail.
    Baseia-se nos thresholds salvos no MongoDB.
    """
    try:
        result = await dispatch_alerts(lat, lon)
        if not result:
            raise HTTPException(status_code=500, detail="Erro ao disparar alertas")
        return {
            "success": True,
            "dispatched": len(result.get("sent", [])),
            "failed": result.get("failed", []),
            "aqi": result.get("aqi"),
            "category": result.get("category"),
            "location": result.get("location", {}),
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.exception("Erro ao enviar alertas: %s", e)
        raise HTTPException(status_code=500, detail=str(e))
