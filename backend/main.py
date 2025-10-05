from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, EmailStr
from typing import Optional
import httpx
import os
from datetime import datetime
import firebase_admin
from firebase_admin import credentials, firestore
from dotenv import load_dotenv
from datetime import timedelta

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

# Credenciais Meteomatics
METEOMATICS_USER = os.getenv("METEOMATICS_USER")
METEOMATICS_PASSWORD = os.getenv("METEOMATICS_PASSWORD")

# Inicializar Firebase (opcional - pode rodar sem Firebase)
db = None
try:
    firebase_json_path = os.getenv("FIREBASE_JSON_PATH", "serviceAccountKey.json")

    if os.path.exists(firebase_json_path):
        cred = credentials.Certificate(firebase_json_path)
        firebase_admin.initialize_app(cred)
        db = firestore.client()
        print("✅ Firebase Firestore conectado com sucesso!")
    else:
        firebase_config = {
            "type": "service_account",
            "project_id": os.getenv("FIREBASE_PROJECT_ID"),
            "private_key_id": os.getenv("FIREBASE_PRIVATE_KEY_ID"),
            "private_key": os.getenv("FIREBASE_PRIVATE_KEY", "").replace("\\n", "\n"),
            "client_email": os.getenv("FIREBASE_CLIENT_EMAIL"),
            "client_id": os.getenv("FIREBASE_CLIENT_ID"),
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token",
            "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
        }

        if all([firebase_config["project_id"], firebase_config["private_key"], firebase_config["client_email"]]):
            cred = credentials.Certificate(firebase_config)
            firebase_admin.initialize_app(cred)
            db = firestore.client()
            print("✅ Firebase inicializado com variáveis de ambiente")
        else:
            print("⚠️  Firebase não configurado - endpoint /subscribe não funcionará")
except Exception as e:
    print(f"⚠️  Firebase não disponível: {e}")
    print("⚠️  A API funcionará sem persistência de dados")


# Models
class EmailSubscription(BaseModel):
    email: EmailStr
    name: Optional[str] = None
    location: Optional[str] = None
    profile: Optional[str] = None
    thresholds: Optional[dict] = None


# Rotas
@app.get("/")
async def root():
    """Rota raiz com informações da API"""
    return {
        "message": "Weather & Air Quality API - NASA Space Apps Challenge 2025",
        "status": "online",
        "database": "Firebase Firestore" if db else "Not configured",
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
            "firebase": "ok" if db else "not configured"
        }
    }


@app.get("/weather")
async def get_weather(lat: float, lon: float):
    """
    Obtém dados meteorológicos das últimas 48h e próximas 48h via Meteomatics
    """
    if not METEOMATICS_USER or not METEOMATICS_PASSWORD:
        raise HTTPException(status_code=503, detail="Meteomatics API não configurada")

    if not (-90 <= lat <= 90):
        raise HTTPException(status_code=400, detail="Latitude inválida")
    if not (-180 <= lon <= 180):
        raise HTTPException(status_code=400, detail="Longitude inválida")

    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            now = datetime.utcnow()
            start_time = (now.replace(microsecond=0)).isoformat() + "Z"
            from_time = (now.replace(microsecond=0) - timedelta(hours=48)).isoformat() + "Z"
            to_time = (now.replace(microsecond=0) + timedelta(hours=48)).isoformat() + "Z"

            params = [
                "t_2m:C",  # temperatura
                "wind_speed_10m:kmh",  # vento
                "wind_dir_10m:d",  # direção
                "relative_humidity_2m:p",  # umidade
                "total_cloud_cover:p",
                "msl_pressure:hPa"
            ]

            params_str = ",".join(params)
            url = f"https://api.meteomatics.com/{from_time}--{to_time}:PT1H/{params_str}/{lat},{lon}/json"

            response = await client.get(url, auth=(METEOMATICS_USER, METEOMATICS_PASSWORD))

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
                "location": {
                    "lat": lat,
                    "lng": lon,
                    "name": get_location_name(lat, lon)
                },
                "timeline": timeline
            }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao buscar dados meteorológicos: {str(e)}")

@app.get("/air")
async def get_air_quality(lat: float, lon: float):
    """
    Obtém dados de qualidade do ar (últimas 48h e próximas 48h)
    """
    if not METEOMATICS_USER or not METEOMATICS_PASSWORD:
        raise HTTPException(status_code=503, detail="Meteomatics API não configurada")

    if not (-90 <= lat <= 90):
        raise HTTPException(status_code=400, detail="Latitude inválida")
    if not (-180 <= lon <= 180):
        raise HTTPException(status_code=400, detail="Longitude inválida")

    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            now = datetime.utcnow()
            from_time = (now.replace(microsecond=0) - timedelta(hours=48)).isoformat() + "Z"
            to_time = (now.replace(microsecond=0) + timedelta(hours=48)).isoformat() + "Z"

            params = [
                "pm2p5:ugm3",
                "pm10:ugm3",
                "no2:ugm3",
                "o3:ugm3",
                "so2:ugm3"
            ]

            params_str = ",".join(params)
            url = f"https://api.meteomatics.com/{from_time}--{to_time}:PT1H/{params_str}/{lat},{lon}/json"

            response = await client.get(url, auth=(METEOMATICS_USER, METEOMATICS_PASSWORD))

            if response.status_code != 200:
                raise HTTPException(status_code=response.status_code, detail=f"Erro Meteomatics: {response.text}")

            data = response.json()
            coordinates = data["data"][0]["coordinates"][0]["dates"]
            timeline = []

            for i in range(len(coordinates)):
                pm25 = data["data"][0]["coordinates"][0]["dates"][i]["value"]
                no2 = data["data"][2]["coordinates"][0]["dates"][i]["value"]
                o3 = data["data"][3]["coordinates"][0]["dates"][i]["value"]
                so2 = data["data"][4]["coordinates"][0]["dates"][i]["value"]

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
                "location": {
                    "lat": lat,
                    "lng": lon,
                    "name": get_location_name(lat, lon)
                },
                "timeline": timeline
            }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao buscar dados de qualidade do ar: {str(e)}")



@app.post("/subscribe")
async def subscribe_email(subscription: EmailSubscription):
    """
    Inscreve um email para receber alertas

    Requer Firebase configurado
    """
    if db is None:
        raise HTTPException(
            status_code=503,
            detail="Firebase não configurado. Configure as credenciais no .env ou serviceAccountKey.json"
        )

    try:
        doc_ref = db.collection("subscriptions").document()

        subscription_data = {
            "email": subscription.email,
            "name": subscription.name,
            "location": subscription.location,
            "profile": subscription.profile,
            "thresholds": subscription.thresholds,
            "subscribed_at": firestore.SERVER_TIMESTAMP,
            "active": True
        }

        doc_ref.set(subscription_data)

        return {
            "success": True,
            "message": "Email inscrito com sucesso!",
            "subscription_id": doc_ref.id,
            "email": subscription.email
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao salvar inscrição: {str(e)}")


@app.get("/subscriptions")
async def list_subscriptions(limit: int = 100):
    """Lista todas as inscrições ativas"""
    if db is None:
        raise HTTPException(status_code=503, detail="Firebase não configurado")

    try:
        subscriptions = []
        docs = db.collection("subscriptions") \
            .where("active", "==", True) \
            .limit(limit) \
            .stream()

        for doc in docs:
            subscription = doc.to_dict()
            subscription["id"] = doc.id
            if "subscribed_at" in subscription and subscription["subscribed_at"]:
                subscription["subscribed_at"] = subscription["subscribed_at"].isoformat() if hasattr(
                    subscription["subscribed_at"], 'isoformat') else str(subscription["subscribed_at"])
            subscriptions.append(subscription)

        return {
            "success": True,
            "total": len(subscriptions),
            "subscriptions": subscriptions
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao listar inscrições: {str(e)}")


# Funções auxiliares
def get_location_name(lat: float, lon: float) -> str:
    """Obtém nome da localização (fallback simples)"""
    known_locations = {
        (-23.5505, -46.6333): "São Paulo, Brazil",
        (40.7128, -74.0060): "New York, USA",
        (51.5074, -0.1278): "London, UK",
        (35.6762, 139.6503): "Tokyo, Japan",
        (-33.8688, 151.2093): "Sydney, Australia",
    }

    for (known_lat, known_lon), name in known_locations.items():
        if abs(lat - known_lat) < 0.1 and abs(lon - known_lon) < 0.1:
            return name

    return f"{lat:.4f}, {lon:.4f}"


def calculate_aqi_from_pm25(pm25: float) -> int:
    """
    Calcula AQI baseado em PM2.5 usando a fórmula US EPA
    """
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
            aqi = ((aqi_hi - aqi_lo) / (bp_hi - bp_lo)) * (pm25 - bp_lo) + aqi_lo
            return round(aqi)

    if pm25 > 500.4:
        return 500

    return 50


def get_aqi_category(aqi: int) -> str:
    """Retorna categoria do AQI"""
    if aqi <= 50:
        return "Good"
    elif aqi <= 100:
        return "Moderate"
    elif aqi <= 150:
        return "Unhealthy for Sensitive Groups"
    elif aqi <= 200:
        return "Unhealthy"
    elif aqi <= 300:
        return "Very Unhealthy"
    else:
        return "Hazardous"


# Startup e Shutdown events
@app.on_event("startup")
async def startup_event():
    """Executado quando a API inicia"""
    print("\n" + "=" * 60)
    print("🚀 Weather & Air Quality API - NASA Space Apps 2025")
    print("=" * 60)
    print(f"✅ FastAPI rodando")
    print(f"{'✅' if METEOMATICS_USER else '❌'} Meteomatics: {'Configurado' if METEOMATICS_USER else 'NÃO configurado'}")
    print(f"{'✅' if db else '⚠️ '} Firebase: {'Conectado' if db else 'NÃO configurado (opcional)'}")
    print("=" * 60)
    print(f"📡 Acesse: http://localhost:8000")
    print(f"📖 Docs: http://localhost:8000/docs")
    print("=" * 60 + "\n")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_level="info"
    )