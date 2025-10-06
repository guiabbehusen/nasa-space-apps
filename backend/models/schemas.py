from pydantic import BaseModel, EmailStr, Field
from typing import Optional, Dict

class EmailSubscription(BaseModel):
    """
    Modelo de inscrição para alertas de qualidade do ar.
    Agora aceita coordenadas (lat/lon), mantendo compatibilidade com 'location'.
    """
    email: EmailStr = Field(..., description="Endereço de e-mail do usuário inscrito")
    lat: Optional[float] = Field(None, description="Latitude da localização do usuário")
    lon: Optional[float] = Field(None, description="Longitude da localização do usuário")
    location: Optional[str] = Field(None, description="Nome da localização (compatibilidade retroativa)")
    profile: Optional[str] = Field(None, description="Perfil de saúde do usuário")
    thresholds: Optional[Dict[str, float]] = Field(default_factory=dict, description="Limiares de alerta configurados pelo usuário")
