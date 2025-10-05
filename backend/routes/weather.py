from fastapi import APIRouter, HTTPException
from services.weather import get_weather_data

router = APIRouter(prefix="/weather", tags=["Weather"])

@router.get("/")
async def get_weather(lat: float, lon: float):
    """
    Retorna dados meteorológicos atuais e previstos para uma coordenada.
    """
    try:
        return await get_weather_data(lat, lon)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
