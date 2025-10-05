from fastapi import HTTPException
from core.meteomatics import fetch_meteomatics
from core.utils import calculate_aqi_from_pm25, get_aqi_category, get_location_name
import logging

logger = logging.getLogger("air-api")

async def get_air_quality_data(lat: float, lon: float):
    if not (-90 <= lat <= 90) or not (-180 <= lon <= 180):
        raise HTTPException(status_code=400, detail="Coordenadas inválidas")

    params = ["pm2p5:ugm3", "pm10:ugm3", "no2:ugm3", "o3:ugm3", "so2:ugm3"]
    try:
        data = await fetch_meteomatics(params, lat, lon, hours=48)

        coordinates = data["data"][0]["coordinates"][0]["dates"]
        timeline = []

        for i in range(len(coordinates)):
            try:
                pm25 = data["data"][0]["coordinates"][0]["dates"][i]["value"]
                pm10 = data["data"][1]["coordinates"][0]["dates"][i]["value"]
                no2  = data["data"][2]["coordinates"][0]["dates"][i]["value"]
                o3   = data["data"][3]["coordinates"][0]["dates"][i]["value"]
                so2  = data["data"][4]["coordinates"][0]["dates"][i]["value"]
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
                    "pm10": round(pm10, 1),
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
