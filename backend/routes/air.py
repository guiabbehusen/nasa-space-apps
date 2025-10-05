from fastapi import APIRouter, HTTPException
from services.air_quality import get_air_quality_data

router = APIRouter(prefix="/air", tags=["Air Quality"])

@router.get("/")
async def get_air(lat: float, lon: float):
    """
    Retorna dados de qualidade do ar (PM2.5, PM10, NO₂, O₃, SO₂, AQI e categoria).
    """
    try:
        return await get_air_quality_data(lat, lon)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
