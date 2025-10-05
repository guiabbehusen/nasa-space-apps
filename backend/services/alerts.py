import asyncio
import logging
from core.database import db
from core.email_utils import send_email
from services.air_quality import get_air_quality_data
from services.slm import generate_air_quality_email

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

    sent = []
    failed = []

    cursor = db["subscriptions"].find({"active": True})
    tasks = []

    for sub in cursor:
        email = sub.get("email")
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

        subject = f"Alerta de Qualidade do Ar: {category} (AQI {aqi_value})"
        body = await generate_air_quality_email(
            name=sub.get("profile"),
            location_name=air_data["location"]["name"],
            aqi=aqi_value,
            category=category,
            timestamp=timestamp,
        )

        async def send_and_collect(email_addr, subj, msg):
            try:
                await asyncio.to_thread(send_email, subj, msg, email_addr)
                logger.info("✅ Email enviado para %s", email_addr)
                return {"ok": True, "email": email_addr}
            except Exception as e:
                logger.exception("Erro ao enviar email: %s", e)
                return {"ok": False, "email": email_addr, "error": str(e)}

        tasks.append(send_and_collect(email, subject, body))

    results = await asyncio.gather(*tasks)
    for r in results:
        if r["ok"]:
            sent.append(r["email"])
        else:
            failed.append(r)

    return {
        "dispatched": len(sent),
        "failed": failed,
        "aqi": aqi_value,
        "category": category,
        "timestamp": timestamp,
        "location": air_data.get("location"),
    }
