import asyncio
from core.database import db
from core.email_utils import send_email
from services.air_quality import get_air_quality_data
from services.slm import generate_air_quality_email
import logging

logger = logging.getLogger("air-api")

async def dispatch_alerts(lat: float, lon: float):
    if db is None:
        return {"error": "MongoDB não configurado"}

    air_data = await get_air_quality_data(lat, lon)
    latest = air_data["timeline"][0]
    aqi = latest["aqi"]
    category = latest["category"]

    sent, failed = [], []

    cursor = db["subscriptions"].find({"active": True})
    tasks = []

    for sub in cursor:
        thresholds = sub.get("thresholds", {}) or {}
        limit = thresholds.get("aqi")

        if limit and aqi < limit:
            continue

        subject = f"Alerta: {category} (AQI {aqi})"
        body = await generate_air_quality_email(sub.get("profile"), air_data["location"]["name"], aqi, category, latest["timestamp"])

        async def send_task(email):
            try:
                await asyncio.to_thread(send_email, subject, body, email)
                sent.append(email)
            except Exception as e:
                failed.append({"email": email, "error": str(e)})

        tasks.append(send_task(sub["email"]))

    await asyncio.gather(*tasks)
    return {"sent": sent, "failed": failed, "aqi": aqi, "category": category}
