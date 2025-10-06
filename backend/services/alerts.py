import asyncio
import logging
from core.database import db
from services.air_quality import get_air_quality_data

logger = logging.getLogger("air-api")

async def dispatch_alerts(lat: float, lon: float):
    if db is None:
        raise RuntimeError("MongoDB não configurado")

    air_data = await get_air_quality_data(lat, lon)
    timeline = air_data.get("timeline", [])
    if not timeline:
        raise RuntimeError("Sem dados de qualidade do ar")

    latest = timeline[0]
    aqi_value = latest.get("aqi")
    category = latest.get("category")
    timestamp = latest.get("timestamp")

    dispatched = 0
    failed = []

    cursor = db["subscriptions"].find({"active": True})
    async for sub in cursor:
        thresholds = sub.get("thresholds", {}) or {}
        should_alert = False

        # Threshold numérico
        if "aqi" in thresholds and isinstance(thresholds["aqi"], (int, float)):
            if aqi_value >= thresholds["aqi"]:
                should_alert = True

        # Threshold por categoria
        if not should_alert and isinstance(thresholds.get("category"), str):
            if category.lower() == thresholds["category"].strip().lower():
                should_alert = True

        if not should_alert:
            continue

        # Aqui você poderia salvar o alerta em outra coleção, se quiser registrar
        try:
            await db["alerts_log"].insert_one({
                "subscription_id": sub["_id"],
                "lat": lat,
                "lon": lon,
                "aqi": aqi_value,
                "category": category,
                "timestamp": timestamp,
            })
            dispatched += 1
        except Exception as e:
            logger.error("Erro ao registrar alerta: %s", e)
            failed.append({"subscription": str(sub.get("_id")), "error": str(e)})

    return {
        "dispatched": dispatched,
        "failed": failed,
        "aqi": aqi_value,
        "category": category,
        "timestamp": timestamp,
        "lat": lat,
        "lon": lon,
    }
