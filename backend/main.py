from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, EmailStr
from typing import Optional
import httpx
import os
from datetime import datetime, timedelta
from dotenv import load_dotenv
import smtplib
from email.mime.text import MIMEText
from email.utils import formataddr
from textwrap import dedent
from pymongo import MongoClient

# Carregar variáveis de ambiente
load_dotenv()

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
        print(f"✅ MongoDB conectado: {db.name}")
    except Exception as e:
        print(f"⚠️  Falha ao conectar ao MongoDB: {e}")
else:
    print("⚠️  MongoDB não configurado - defina MONGO_URI no .env")

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

# SLM / OpenAI
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# ============================================================
# 🧩 Models
# ============================================================
class EmailSubscription(BaseModel):
    email: EmailStr
    location: Optional[str] = None
    profile: Optional[str] = None
    thresholds: Optional[dict] = None

# ============================================================
# 🌍 Rotas principais
# ============================================================
@app.get("/")
def root():
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
def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "services": {
            "meteomatics": "ok" if METEOMATICS_USER else "not configured",
            "mongodb": "ok" if db is not None else "not configured",
            "email": "ok" if SMTP_HOST and SMTP_USER and SMTP_PASSWORD else "not configured",
            "slm": "ok" if OPENAI_API_KEY else "not configured"
        }
    }

# ============================================================
# 🌦️ Endpoint: Weather
# ============================================================
@app.get("/weather")
def get_weather(lat: float, lon: float):
    if not METEOMATICS_USER or not METEOMATICS_PASSWORD:
        raise HTTPException(status_code=503, detail="Meteomatics API não configurada")

    if not (-90 <= lat <= 90) or not (-180 <= lon <= 180):
        raise HTTPException(status_code=400, detail="Coordenadas inválidas")

    try:
        now = datetime.utcnow().replace(microsecond=0)
        from_time = (now - timedelta(hours=48)).isoformat() + "Z"
        to_time = (now + timedelta(hours=48)).isoformat() + "Z"

        params = [
            "t_2m:C",
            "wind_speed_10m:kmh",
            "wind_dir_10m:d",
            "relative_humidity_2m:p",
            "total_cloud_cover:p",
            "msl_pressure:hPa"
        ]
        params_str = ",".join(params)
        url = f"https://api.meteomatics.com/{from_time}--{to_time}:PT1H/{params_str}/{lat},{lon}/json"

        response = httpx.get(url, auth=(METEOMATICS_USER, METEOMATICS_PASSWORD), timeout=60.0)

        if response.status_code != 200:
            raise HTTPException(status_code=response.status_code, detail=f"Erro Meteomatics: {response.text}")

        data = response.json()
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

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao buscar dados meteorológicos: {e}")

# ============================================================
# 💨 Endpoint: Air Quality
# ============================================================
@app.get("/air")
def get_air_quality(lat: float, lon: float):
    if not METEOMATICS_USER or not METEOMATICS_PASSWORD:
        raise HTTPException(status_code=503, detail="Meteomatics API não configurada")

    if not (-90 <= lat <= 90) or not (-180 <= lon <= 180):
        raise HTTPException(status_code=400, detail="Coordenadas inválidas")

    try:
        now = datetime.utcnow().replace(microsecond=0)
        from_time = (now - timedelta(hours=48)).isoformat() + "Z"
        to_time = (now + timedelta(hours=48)).isoformat() + "Z"

        params = ["pm2p5:ugm3", "pm10:ugm3", "no2:ugm3", "o3:ugm3", "so2:ugm3"]
        params_str = ",".join(params)
        url = f"https://api.meteomatics.com/{from_time}--{to_time}:PT1H/{params_str}/{lat},{lon}/json"

        response = httpx.get(url, auth=(METEOMATICS_USER, METEOMATICS_PASSWORD), timeout=60.0)
        if response.status_code != 200:
            raise HTTPException(status_code=response.status_code, detail=f"Erro Meteomatics: {response.text}")

        data = response.json()
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

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao buscar qualidade do ar: {e}")


# ============================================================
# ✉️ Utilitário de envio de e-mail
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

# ============================================================
# 📧 Endpoint: Inscrição no MongoDB
# ============================================================
@app.post("/subscribe")
def subscribe_email(subscription: EmailSubscription):
    if db is None:
        raise HTTPException(status_code=503, detail="MongoDB não configurado")

    try:
        # Validação simples de thresholds
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
        raise HTTPException(status_code=500, detail=f"Erro ao salvar inscrição: {e}")


# ============================================================
# 🚨 Endpoint: Disparar alertas por e-mail
# ============================================================
@app.post("/alerts/dispatch")
def dispatch_alerts(lat: float, lon: float):
    if db is None:
        raise HTTPException(status_code=503, detail="MongoDB não configurado")
    if not (SMTP_HOST and SMTP_USER and SMTP_PASSWORD):
        raise HTTPException(status_code=503, detail="SMTP não configurado")

    # Obter a timeline de AQI para a localização
    air_data = get_air_quality(lat, lon)
    timeline = air_data.get("timeline", [])
    if not timeline:
        raise HTTPException(status_code=502, detail="Sem dados de qualidade do ar")

    # Usar o valor mais recente
    latest = timeline[0]
    aqi_value = latest.get("aqi")
    aqi_category = latest.get("category")
    timestamp = latest.get("timestamp")

    sent = []
    failed = []

    # Iterar inscrições ativas
    cursor = db["subscriptions"].find({"active": True})
    for sub in cursor:
        email = sub.get("email")
        thresholds = sub.get("thresholds", {}) or {}
        alert_threshold = None

        # Interpretar threshold por AQI numérico
        if isinstance(thresholds, dict):
            if "aqi" in thresholds and isinstance(thresholds["aqi"], (int, float)):
                alert_threshold = thresholds["aqi"]

        should_alert = False
        if aqi_value is not None and alert_threshold is not None and aqi_value >= alert_threshold:
            should_alert = True

        # Alternativamente, permitir threshold por categoria
        if not should_alert and isinstance(thresholds.get("category"), str):
            desired_cat = thresholds["category"].strip().lower()
            if isinstance(aqi_category, str) and aqi_category.strip().lower() == desired_cat:
                should_alert = True

        if not should_alert:
            continue

        subject = f"Alerta de Qualidade do Ar: {aqi_category} (AQI {aqi_value})"
        body = render_slm_message(
            name=sub.get("name") or sub.get("profile"),
            location_name=air_data["location"]["name"],
            aqi=aqi_value,
            category=aqi_category,
            timestamp=timestamp,
        )

        try:
            send_email(subject, body, email)
            sent.append(email)
        except Exception as e:
            failed.append({"email": email, "error": str(e)})

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
# 🧾 Endpoint: Listagem de inscrições
# ============================================================
@app.get("/subscriptions")
def list_subscriptions(limit: int = 100):
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
        raise HTTPException(status_code=500, detail=f"Erro ao listar inscrições: {e}")

# ============================================================
# 🧠 Funções auxiliares
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


def render_slm_message(name: str, location_name: str, aqi: int, category: str, timestamp: str) -> str:
    if not OPENAI_API_KEY:
        return render_rule_based_message(name, location_name, aqi, category, timestamp)

    # Lazy import to avoid hard dependency when not configured
    try:
        from openai import OpenAI  # type: ignore
    except Exception:
        return render_rule_based_message(name, location_name, aqi, category, timestamp)

    prompt = dedent(f"""
        Você é um assistente que escreve e-mails curtos, claros e empáticos em PT-BR.
        Gere um e-mail de notificação de alerta de qualidade do ar personalizado.

        Requisitos:
        - Tom: cordial, direto, 100-150 palavras
        - Inclua: local, timestamp, categoria, AQI numérico
        - 1-2 recomendações práticas para a categoria
        - Assinatura curta

        Dados:
        - Nome: {name or 'usuário'}
        - Local: {location_name}
        - Timestamp: {timestamp}
        - Categoria: {category}
        - AQI: {aqi}
    """)

    try:
        client = OpenAI(api_key=OPENAI_API_KEY)
        completion = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "Você cria e-mails curtos, claros e empáticos."},
                {"role": "user", "content": prompt},
            ],
            temperature=0.7,
            max_tokens=280,
        )
        content = completion.choices[0].message.content or ""
        return content.strip() or render_rule_based_message(name, location_name, aqi, category, timestamp)
    except Exception:
        return render_rule_based_message(name, location_name, aqi, category, timestamp)

# ============================================================
# 🚀 Startup
# ============================================================
@app.on_event("startup")
def startup_event():
    print("\n" + "=" * 60)
    print("🚀 Weather & Air Quality API - NASA Space Apps 2025")
    print("=" * 60)
    print(f"✅ FastAPI rodando")
    print(f"{'✅' if METEOMATICS_USER else '❌'} Meteomatics: {'Configurado' if METEOMATICS_USER else 'NÃO configurado'}")
    print(f"{'✅' if db is not None else '⚠️ '} MongoDB: {'Conectado' if db is not None else 'NÃO configurado'}")
    print("=" * 60)
    print("📡 http://localhost:8000")
    print("📖 Docs: http://localhost:8000/docs")
    print("=" * 60 + "\n")

# ============================================================
# 🏁 Execução local
# ============================================================
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")
