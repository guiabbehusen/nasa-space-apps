from fastapi import APIRouter, HTTPException
from services.alerts import dispatch_alerts
import logging

router = APIRouter(prefix="/alerts", tags=["Alerts"])
logger = logging.getLogger("air-api")

@router.post("/dispatch")
async def trigger_alerts(lat: float, lon: float):
    """
    Dispara alertas de qualidade do ar com base nas coordenadas (lat, lon).
    Baseia-se nos thresholds salvos no MongoDB.
    """
    try:
        result = await dispatch_alerts(lat, lon)
        if not result:
            raise HTTPException(status_code=500, detail="Erro ao disparar alertas")
        return {
            "success": True,
            "dispatched": result.get("dispatched", 0),
            "failed": result.get("failed", []),
            "aqi": result.get("aqi"),
            "category": result.get("category"),
            "timestamp": result.get("timestamp"),
            "lat": result.get("lat"),
            "lon": result.get("lon"),
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.exception("Erro ao processar alertas: %s", e)
        raise HTTPException(status_code=500, detail=str(e))
