import asyncio
import logging
from textwrap import dedent
from core.config import SLM_PROVIDER, OLLAMA_MODEL
from core.utils import get_aqi_category

logger = logging.getLogger("air-api")

def render_rule_based_message(name: str, location_name: str, aqi: int, category: str, timestamp: str) -> str:
    """Gera mensagem de e-mail com base em regras fixas."""
    recommendations = {
        "Good": "Aproveite atividades ao ar livre normalmente.",
        "Moderate": "Sensíveis devem reduzir exposição prolongada.",
        "Unhealthy for Sensitive Groups": "Pessoas sensíveis devem limitar atividades intensas.",
        "Unhealthy": "Evite atividades ao ar livre; use máscara se necessário.",
        "Very Unhealthy": "Fique em locais fechados com filtragem de ar.",
        "Hazardous": "Emergência: evite sair de casa."
    }

    tip = recommendations.get(category, "Fique atento às orientações locais.")
    greeting = f"Olá {name or ''},".strip()
    return (
        f"{greeting}\n\nAlerta de Qualidade do Ar em {location_name} ({timestamp}).\n"
        f"Categoria: {category}\nAQI: {aqi}\n\nRecomendação: {tip}\n\n"
        "Você pode ajustar seus alertas nas preferências."
    )

async def generate_air_quality_email(name, location_name, aqi, category, timestamp):
    """Tenta usar Ollama; se falhar, gera mensagem rule-based."""
    if SLM_PROVIDER != "ollama":
        return render_rule_based_message(name, location_name, aqi, category, timestamp)

    prompt = dedent(f"""
        You are an assistant that writes short, clear, and empathetic emails.
        Generate a friendly air quality alert email for:
        - Name: {name or 'user'}
        - Location: {location_name}
        - AQI: {aqi}
        - Category: {category}
        - Timestamp: {timestamp}
        Include emojis and practical recommendations.
    """)

    try:
        import ollama
        def sync_call():
            response = ollama.chat(
                model=OLLAMA_MODEL,
                messages=[{"role": "user", "content": prompt}],
                options={"temperature": 0.7},
            )
            return (response.get("message", {}).get("content", "") or "").strip()

        return await asyncio.to_thread(sync_call)
    except Exception as e:
        logger.warning("Erro ao chamar Ollama: %s", e)
        return render_rule_based_message(name, location_name, aqi, category, timestamp)
