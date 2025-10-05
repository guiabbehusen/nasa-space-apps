import asyncio
import logging
from textwrap import dedent
from core.config import SLM_PROVIDER, OLLAMA_MODEL
from core.utils import get_aqi_category

logger = logging.getLogger("air-api")

async def generate_air_quality_email(name, location_name, aqi, category, timestamp):
    prompt = dedent(f"""
        Write a short friendly email (100–150 words) alerting {name or 'user'}
        about the air quality in {location_name} at {timestamp}.
        AQI: {aqi} ({category})
        Add emojis and practical tips.
    """)

    if SLM_PROVIDER != "ollama":
        return f"Alerta de Qualidade do Ar: {category} (AQI {aqi}) em {location_name}."

    try:
        import ollama
        def sync_call():
            response = ollama.chat(
                model=OLLAMA_MODEL,
                messages=[{"role": "user", "content": prompt}],
                options={"temperature": 0.7},
            )
            return response["message"]["content"].strip()
        return await asyncio.to_thread(sync_call)
    except Exception as e:
        logger.error("Erro ao chamar Ollama: %s", e)
        return f"Qualidade do ar {category} em {location_name}. AQI {aqi}."
