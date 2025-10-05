import httpx
import asyncio
from datetime import datetime, timedelta
from core.config import METEOMATICS_USER, METEOMATICS_PASSWORD
import logging

logger = logging.getLogger("air-api")

def build_meteomatics_url(from_time_iso: str, to_time_iso: str, params_str: str, lat: float, lon: float) -> str:
    return f"https://api.meteomatics.com/{from_time_iso}--{to_time_iso}:PT1H/{params_str}/{lat},{lon}/json"

async def fetch_meteomatics(params, lat, lon, hours=48, retries=2):
    if not METEOMATICS_USER or not METEOMATICS_PASSWORD:
        raise RuntimeError("Meteomatics API não configurada")

    now = datetime.utcnow().replace(microsecond=0)
    from_time = (now - timedelta(hours=hours)).isoformat() + "Z"
    to_time = (now + timedelta(hours=hours)).isoformat() + "Z"
    params_str = ",".join(params)
    url = build_meteomatics_url(from_time, to_time, params_str, lat, lon)

    for attempt in range(retries + 1):
        try:
            async with httpx.AsyncClient(timeout=60.0) as client:
                resp = await client.get(url, auth=(METEOMATICS_USER, METEOMATICS_PASSWORD))
                resp.raise_for_status()
                return resp.json()
        except Exception as e:
            logger.warning("Erro ao consultar Meteomatics (%s): %s", attempt, e)
            await asyncio.sleep(1 + attempt)
    raise RuntimeError("Erro ao buscar dados da Meteomatics")
