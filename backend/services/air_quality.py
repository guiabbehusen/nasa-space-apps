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
        data = await fetch_meteomatics(params, lat, lon)
        coords = data["data"][0]["coordinates"][0]["dates"]

        timeline = []
        for i in range(len(coords)):
            pm25 = data["data"][0]["coordinates"][0]["dates"][i]["value"]
            aqi = calculate_aqi_from_pm25(pm25)
            timeline.append({
                "timestamp": coords[i]["date"],
                "aqi": aqi,
                "category": get_aqi_category(aqi)
            })

        return {"location": {"lat": lat, "lng": lon, "name": get_location_name(lat, lon)}, "timeline": timeline}
    except Exception as e:
        logger.exception(e)
        raise HTTPException(status_code=500, detail=f"Erro ao buscar qualidade do ar: {e}")
