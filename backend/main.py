from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, EmailStr
from typing import Optional, List, Dict, Any
import httpx
import os
from datetime import datetime, timedelta
from dotenv import load_dotenv
import smtplib
from email.mime.text import MIMEText
from email.utils import formataddr
from pymongo import MongoClient
import asyncio
import logging
from textwrap import dedent

# Carregar variáveis de ambiente
load_dotenv()

# ---------- Logging ----------
logging.basicConfig(
    level=os.getenv("LOG_LEVEL", "INFO"),
    format="%(asctime)s %(levelname)s %(name)s - %(message)s"
)
logger = logging.getLogger("air-api")

# Inicializar FastAPI
app = FastAPI(
    title="Weather & Air Quality API - NASA Space Apps 2025",
    description="API para dados meteorológicos e qualidade do ar usando Meteomatics",
    version="1.0.0"
)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configuração do MongoDB (PyMongo)
MONGO_URI = os.getenv("MONGO_URI")
MONGO_DB_NAME = os.getenv("MONGO_DB_NAME", "users")

db = None
if MONGO_URI:
    try:
        client = MongoClient(MONGO_URI)
        db = client[MONGO_DB_NAME]
        logger.info("✅ MongoDB conectado: %s", db.name)
    except Exception as e:
        logger.exception("⚠️  Falha ao conectar ao MongoDB: %s", e)
else:
    logger.warning("⚠️  MongoDB não configurado - defina MONGO_URI no .env")

# Configuração de E-mail (SMTP)
SMTP_HOST = os.getenv("SMTP_HOST")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
SMTP_USER = os.getenv("SMTP_USER")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD")
SMTP_FROM_NAME = os.getenv("SMTP_FROM_NAME", "Air Alerts")
SMTP_FROM_EMAIL = os.getenv("SMTP_FROM_EMAIL", SMTP_USER or "noreply@example.com")

# Credenciais Meteomatics
METEOMATICS_USER = os.getenv("METEOMATICS_USER")
METEOMATICS_PASSWORD = os.getenv("METEOMATICS_PASSWORD")

# SLM Provider
SLM_PROVIDER = os.getenv("SLM_PROVIDER", "ollama").lower()  # ollama (default)
OLLAMA_HOST = os.getenv("OLLAMA_HOST", "http://localhost:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "qwen2.5-coder:1.5b")

# ============================================================
# 🧩 Models
# ============================================================
class EmailSubscription(BaseModel):
    email: EmailStr
    location: Optional[str] = None
    profile: Optional[str] = None
    thresholds: Optional[dict] = None

# ============================================================
# 🌍 Rotas principais (mantive nomes/assinaturas)
# ============================================================
@app.get("/")
async def root():
    """Rota raiz com informações da API"""
    return {
        "message": "Weather & Air Quality API - NASA Space Apps Challenge 2025",
        "status": "online",
        "database": f"MongoDB ({db.name})" if db is not None else "Not configured",
        "weather_api": "Meteomatics" if METEOMATICS_USER else "Not configured",
        "endpoints": {
            "health": "GET /health",
            "weather": "GET /weather?lat={latitude}&lon={longitude}",
            "air": "GET /air?lat={latitude}&lon={longitude}",
            "subscribe": "POST /subscribe",
            "subscriptions": "GET /subscriptions"
        }
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "services": {
            "meteomatics": "ok" if METEOMATICS_USER else "not configured",
            "mongodb": "ok" if db is not None else "not configured",
            "email": "ok" if SMTP_HOST and SMTP_USER and SMTP_PASSWORD else "not configured",
            "slm": {
                "provider": "ollama",
                "status": "ok" if SLM_PROVIDER == "ollama" else "not configured",
                "model": OLLAMA_MODEL
            }
        }
    }

# ============================================================
# 🧠 Utilitários internos (mantendo nomes públicos onde aplicável)
# ============================================================
def get_location_name(lat: float, lon: float) -> str:
    known_locations = {
        (-23.5505, -46.6333): "São Paulo, Brazil",
        (40.7128, -74.0060): "New York, USA",
        (51.5074, -0.1278): "London, UK",
        (35.6762, 139.6503): "Tokyo, Japan",
        (-33.8688, 151.2093): "Sydney, Australia"
    }
    for (k_lat, k_lon), name in known_locations.items():
        if abs(lat - k_lat) < 0.1 and abs(lon - k_lon) < 0.1:
            return name
    return f"{lat:.4f}, {lon:.4f}"

def calculate_aqi_from_pm25(pm25: float) -> int:
    breakpoints = [
        (0.0, 12.0, 0, 50),
        (12.1, 35.4, 51, 100),
        (35.5, 55.4, 101, 150),
        (55.5, 150.4, 151, 200),
        (150.5, 250.4, 201, 300),
        (250.5, 500.4, 301, 500)
    ]
    for bp_lo, bp_hi, aqi_lo, aqi_hi in breakpoints:
        if bp_lo <= pm25 <= bp_hi:
            return round(((aqi_hi - aqi_lo) / (bp_hi - bp_lo)) * (pm25 - bp_lo) + aqi_lo)
    return 500 if pm25 > 500.4 else 50

def get_aqi_category(aqi: int) -> str:
    if aqi <= 50: return "Good"
    elif aqi <= 100: return "Moderate"
    elif aqi <= 150: return "Unhealthy for Sensitive Groups"
    elif aqi <= 200: return "Unhealthy"
    elif aqi <= 300: return "Very Unhealthy"
    else: return "Hazardous"

def render_rule_based_message(name: str, location_name: str, aqi: int, category: str, timestamp: str) -> str:
    recommendations = {
        "Good": "Aproveite atividades ao ar livre normalmente.",
        "Moderate": "Sensíveis devem considerar reduzir exposição prolongada ao ar livre.",
        "Unhealthy for Sensitive Groups": "Pessoas sensíveis devem limitar atividades intensas ao ar livre.",
        "Unhealthy": "Evite atividades ao ar livre; considere usar máscara.",
        "Very Unhealthy": "Permaneça em ambientes internos com filtragem de ar.",
        "Hazardous": "Emergência: evite sair e garanta vedação/filtragem do ar."
    }

    tip = recommendations.get(category, "Fique atento às orientações locais.")
    greeting_name = name or ""
    greeting = f"Olá {greeting_name},".strip()
    body = f"\n\nAlerta de Qualidade do Ar em {location_name} ({timestamp}).\nCategoria: {category}\nAQI: {aqi}\n\nRecomendação: {tip}\n\n"  # noqa: E501
    footer = "Você pode ajustar seus alertas nas preferências."
    return f"{greeting}{body}{footer}"

# ---------- Meteomatics helper ----------
def build_meteomatics_url(from_time_iso: str, to_time_iso: str, params_str: str, lat: float, lon: float) -> str:
    return f"https://api.meteomatics.com/{from_time_iso}--{to_time_iso}:PT1H/{params_str}/{lat},{lon}/json"

async def fetch_meteomatics(params: List[str], lat: float, lon: float, hours: int = 48, retries: int = 2) -> Dict[str, Any]:
    if not METEOMATICS_USER or not METEOMATICS_PASSWORD:
        raise RuntimeError("Meteomatics API não configurada")

    now = datetime.utcnow().replace(microsecond=0)
    from_time = (now - timedelta(hours=hours)).isoformat() + "Z"
    to_time = (now + timedelta(hours=hours)).isoformat() + "Z"
    params_str = ",".join(params)
    url = build_meteomatics_url(from_time, to_time, params_str, lat, lon)

    last_exc = None
    for attempt in range(retries + 1):
        try:
            async with httpx.AsyncClient(timeout=60.0) as client:
                resp = await client.get(url, auth=(METEOMATICS_USER, METEOMATICS_PASSWORD))
                if resp.status_code != 200:
                    logger.warning("Meteomatics response status %s (attempt %s): %s", resp.status_code, attempt, resp.text)
                    resp.raise_for_status()
                data = resp.json()
                return data
        except Exception as e:
            last_exc = e
            logger.exception("Erro ao consultar Meteomatics (attempt %s): %s", attempt, e)
            await asyncio.sleep(1 + attempt * 1.0)
    raise last_exc if last_exc else RuntimeError("Erro desconhecido ao consultar Meteomatics")

# ============================================================
# 🌦️ Endpoint: Weather (refatorado para async mantendo assinatura)
# ============================================================
@app.get("/weather")
async def get_weather(lat: float, lon: float):
    if not METEOMATICS_USER or not METEOMATICS_PASSWORD:
        raise HTTPException(status_code=503, detail="Meteomatics API não configurada")

    if not (-90 <= lat <= 90) or not (-180 <= lon <= 180):
        raise HTTPException(status_code=400, detail="Coordenadas inválidas")

    try:
        params = [
            "t_2m:C",
            "wind_speed_10m:kmh",
            "wind_dir_10m:d",
            "relative_humidity_2m:p",
            "total_cloud_cover:p",
            "msl_pressure:hPa"
        ]
        data = await fetch_meteomatics(params, lat, lon, hours=48)

        # mesmo parsing que havia originalmente (mantive estrutura)
        coordinates = data["data"][0]["coordinates"][0]["dates"]

        timeline = []
        for i in range(len(coordinates)):
            entry = {"timestamp": coordinates[i]["date"]}
            for j, param in enumerate(params):
                try:
                    value = data["data"][j]["coordinates"][0]["dates"][i]["value"]
                except (IndexError, KeyError):
                    value = None
                name = param.split(":")[0]
                entry[name] = value
            timeline.append(entry)

        return {
            "location": {"lat": lat, "lng": lon, "name": get_location_name(lat, lon)},
            "timeline": timeline
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.exception("Erro ao buscar dados meteorológicos: %s", e)
        raise HTTPException(status_code=500, detail=f"Erro ao buscar dados meteorológicos: {e}")

# ============================================================
# 💨 Endpoint: Air Quality (refatorado para async mantendo assinatura)
# ============================================================
@app.get("/air")
async def get_air_quality(lat: float, lon: float):
    if not METEOMATICS_USER or not METEOMATICS_PASSWORD:
        raise HTTPException(status_code=503, detail="Meteomatics API não configurada")

    if not (-90 <= lat <= 90) or not (-180 <= lon <= 180):
        raise HTTPException(status_code=400, detail="Coordenadas inválidas")

    try:
        params = ["pm2p5:ugm3", "pm10:ugm3", "no2:ugm3", "o3:ugm3", "so2:ugm3"]
        data = await fetch_meteomatics(params, lat, lon, hours=48)

        coordinates = data["data"][0]["coordinates"][0]["dates"]
        timeline = []

        for i in range(len(coordinates)):
            try:
                pm25 = data["data"][0]["coordinates"][0]["dates"][i]["value"]
                no2 = data["data"][2]["coordinates"][0]["dates"][i]["value"]
                o3 = data["data"][3]["coordinates"][0]["dates"][i]["value"]
                so2 = data["data"][4]["coordinates"][0]["dates"][i]["value"]
            except (IndexError, KeyError):
                continue

            aqi = calculate_aqi_from_pm25(pm25)
            category = get_aqi_category(aqi)

            timeline.append({
                "timestamp": coordinates[i]["date"],
                "aqi": aqi,
                "category": category,
                "pollutants": {
                    "pm25": round(pm25, 1),
                    "no2": round(no2, 1),
                    "o3": round(o3, 1),
                    "so2": round(so2, 1)
                }
            })

        return {
            "location": {"lat": lat, "lng": lon, "name": get_location_name(lat, lon)},
            "timeline": timeline
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.exception("Erro ao buscar qualidade do ar: %s", e)
        raise HTTPException(status_code=500, detail=f"Erro ao buscar qualidade do ar: {e}")

# ============================================================
# ✉️ Utilitário de envio de e-mail (mantive o mesmo comportamento)
# ============================================================
def send_email(subject: str, body: str, to_email: str) -> None:
    if not (SMTP_HOST and SMTP_USER and SMTP_PASSWORD):
        raise RuntimeError("SMTP não configurado")

    msg = MIMEText(body, "plain", "utf-8")
    msg["Subject"] = subject
    msg["From"] = formataddr((SMTP_FROM_NAME, SMTP_FROM_EMAIL))
    msg["To"] = to_email

    with smtplib.SMTP(SMTP_HOST, SMTP_PORT, timeout=30) as server:
        server.starttls()
        server.login(SMTP_USER, SMTP_PASSWORD)
        server.send_message(msg)
    logger.debug("Email enviado para %s", to_email)

# ============================================================
# 📧 Endpoint: Inscrição no MongoDB (mantive assinatura)
# ============================================================
@app.post("/subscribe")
async def subscribe_email(subscription: EmailSubscription):
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
        return {
            "success": True,
            "message": "Email inscrito com sucesso!",
            "subscription_id": str(result.inserted_id)
        }

    except Exception as e:
        logger.exception("Erro ao salvar inscrição: %s", e)
        raise HTTPException(status_code=500, detail=f"Erro ao salvar inscrição: {e}")

# ============================================================
# 🧾 Endpoint: Listagem de inscrições (mantive assinatura)
# ============================================================
@app.get("/subscriptions")
async def list_subscriptions(limit: int = 100):
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

# ============================================================
# 🧠 SLM / Ollama integration (mantive nomes e fallback)
# ============================================================
async def generate_air_quality_email_ollama(name: str, location_name: str, aqi: int, category: str, timestamp: str) -> str:
    """
    Chama o Ollama (se disponível) em thread para não bloquear.
    Se falhar, retorna mensagem rule-based.
    """
    prompt = dedent(f"""
        You are an assistant that writes short, clear, and empathetic emails in English.
        Generate a personalized air quality alert notification email.

        Requirements:
        - Tone: friendly, direct, 100–150 words
        - Include: location, timestamp, category, numeric AQI
        - Add 1–2 practical recommendations based on the category
        - End with a short signature

        Data:
        - Name: {name or 'user'}
        - Location: {location_name}
        - Timestamp: {timestamp}
        - Category: {category}
        - AQI: {aqi}
    """)

    if SLM_PROVIDER != "ollama":
        return render_rule_based_message(name, location_name, aqi, category, timestamp)

    try:
        # chamada de biblioteca ollama pode ser bloqueante; rodamos em thread
        def sync_call():
            import ollama  # type: ignore
            response = ollama.chat(
                model=OLLAMA_MODEL or "llama3",
                messages=[
                    {"role": "system", "content": "You write short, clear, and empathetic emails."},
                    {"role": "user", "content": prompt},
                ],
                options={"temperature": 0.7},
            )
            return (response.get("message", {}).get("content", "") or "").strip()

        content = await asyncio.to_thread(sync_call)
        if not content:
            return render_rule_based_message(name, location_name, aqi, category, timestamp)
        return content
    except Exception as e:
        logger.exception("Erro ao chamar Ollama: %s", e)
        return render_rule_based_message(name, location_name, aqi, category, timestamp)

async def render_slm_message(name: str, location_name: str, aqi: int, category: str, timestamp: str) -> str:
    if SLM_PROVIDER == "ollama":
        return await generate_air_quality_email_ollama(name, location_name, aqi, category, timestamp)
    return render_rule_based_message(name, location_name, aqi, category, timestamp)

# ============================================================
# 🚨 Endpoint: Disparar alertas por e-mail (refatorado para async mantendo assinatura)
# ============================================================
@app.post("/alerts/dispatch")
async def dispatch_alerts(lat: float, lon: float):
    if db is None:
        raise HTTPException(status_code=503, detail="MongoDB não configurado")
    if not (SMTP_HOST and SMTP_USER and SMTP_PASSWORD):
        raise HTTPException(status_code=503, detail="SMTP não configurado")

    # Obter a timeline de AQI para a localização (agora async)
    air_data = await get_air_quality(lat, lon)
    timeline = air_data.get("timeline", [])
    if not timeline:
        raise HTTPException(status_code=502, detail="Sem dados de qualidade do ar")

    # Usar o valor mais recente (mantive a mesma lógica/índice para compatibilidade)
    latest = timeline[0]
    aqi_value = latest.get("aqi")
    aqi_category = latest.get("category")
    timestamp = latest.get("timestamp")

    sent = []
    failed = []

    # Iterar inscrições ativas
    cursor = db["subscriptions"].find({"active": True})
    tasks = []

    for sub in cursor:
        email = sub.get("email")
        thresholds = sub.get("thresholds", {}) or {}
        alert_threshold = None

        if isinstance(thresholds, dict):
            if "aqi" in thresholds and isinstance(thresholds["aqi"], (int, float)):
                alert_threshold = thresholds["aqi"]

        should_alert = False
        if aqi_value is not None and alert_threshold is not None and aqi_value >= alert_threshold:
            should_alert = True

        if not should_alert and isinstance(thresholds.get("category"), str):
            desired_cat = thresholds["category"].strip().lower()
            if isinstance(aqi_category, str) and aqi_category.strip().lower() == desired_cat:
                should_alert = True

        if not should_alert:
            continue

        subject = f"Alerta de Qualidade do Ar: {aqi_category} (AQI {aqi_value})"

        # render_slm_message é async
        body = await render_slm_message(
            name=sub.get("name") or sub.get("profile"),
            location_name=air_data["location"]["name"],
            aqi=aqi_value,
            category=aqi_category,
            timestamp=timestamp,
        )

        # para não bloquear, executamos send_email em thread
        async def send_and_collect(email_addr: str, subj: str, bdy: str):
            try:
                await asyncio.to_thread(send_email, subj, bdy, email_addr)
                logger.info("Alert email sent to %s", email_addr)
                return {"ok": True, "email": email_addr}
            except Exception as e:
                logger.exception("Erro ao enviar email para %s: %s", email_addr, e)
                return {"ok": False, "email": email_addr, "error": str(e)}

        tasks.append(send_and_collect(email, subject, body))

    # executar envios concorrentes (limitamos concorrência)
    results = []
    if tasks:
        # limitar concorrência com semáforo
        sem = asyncio.Semaphore(int(os.getenv("EMAIL_CONCURRENCY", "20")))

        async def sem_task(t):
            async with sem:
                return await t

        results = await asyncio.gather(*(sem_task(t) for t in tasks), return_exceptions=False)

    for r in results:
        if r.get("ok"):
            sent.append(r["email"])
        else:
            failed.append({"email": r.get("email"), "error": r.get("error")})

    return {
        "success": True,
        "dispatched": len(sent),
        "failed": failed,
        "aqi": aqi_value,
        "category": aqi_category,
        "timestamp": timestamp,
        "location": air_data.get("location")
    }

# ============================================================
# 🚀 Startup (mantive prints e agora assíncrono)
# ============================================================
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

# ============================================================
# 🏁 Execução local
# ============================================================
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")
