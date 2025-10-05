from fastapi import HTTPException
from core.meteomatics import fetch_meteomatics
from core.utils import get_location_name
import logging

logger = logging.getLogger("air-api")

async def get_weather_data(lat: float, lon: float):
    if not (-90 <= lat <= 90) or not (-180 <= lon <= 180):
        raise HTTPException(status_code=400, detail="Coordenadas inválidas")

    params = ["t_2m:C", "wind_speed_10m:kmh", "wind_dir_10m:d", "relative_humidity_2m:p", "total_cloud_cover:p"]
    try:
        data = await fetch_meteomatics(params, lat, lon)
        coordinates = data["data"][0]["coordinates"][0]["dates"]

        timeline = []
        for i in range(len(coordinates)):
            entry = {"timestamp": coordinates[i]["date"]}
            for j, param in enumerate(params):
                entry[param.split(":")[0]] = data["data"][j]["coordinates"][0]["dates"][i]["value"]
            timeline.append(entry)

        return {"location": {"lat": lat, "lng": lon, "name": get_location_name(lat, lon)}, "timeline": timeline}
    except Exception as e:
        logger.exception(e)
        raise HTTPException(status_code=500, detail=f"Erro ao buscar dados meteorológicos: {e}")
