from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, EmailStr
from typing import Optional
import httpx
import os
from datetime import datetime, timedelta
from dotenv import load_dotenv
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

# Credenciais Meteomatics
METEOMATICS_USER = os.getenv("METEOMATICS_USER")
METEOMATICS_PASSWORD = os.getenv("METEOMATICS_PASSWORD")

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
            "mongodb": "ok" if db is not None else "not configured"
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
# 📧 Endpoint: Inscrição no MongoDB
# ============================================================
@app.post("/subscribe")
def subscribe_email(subscription: EmailSubscription):
    if db is None:
        raise HTTPException(status_code=503, detail="MongoDB não configurado")

    try:
        data = {
            "email": subscription.email,
            "name": subscription.name,
            "location": subscription.location,
            "profile": subscription.profile,
            "thresholds": subscription.thresholds,
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
