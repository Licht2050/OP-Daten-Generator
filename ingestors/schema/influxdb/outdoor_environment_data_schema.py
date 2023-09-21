from pydantic import BaseModel, Field
from datetime import datetime

def reverse_alias_generator(alias: str) -> str:
    mapping = {
        'Außentemperatur': 'external_temperature',
        'Luftfeuchtigkeit': 'air_humidity',
        'Luftdruck': 'air_pressure',
        'Windgeschwindigkeit': 'wind_speed',
    }
    return mapping.get(alias, alias)

class OutdoorEnvironmentValue(BaseModel):
    external_temperature: float = Field(..., alias='Außentemperatur')
    air_humidity: float = Field(..., alias='Luftfeuchtigkeit')
    air_pressure: float = Field(..., alias='Luftdruck')
    wind_speed: float = Field(..., alias='Windgeschwindigkeit')

    class Config:
        alias_generator = reverse_alias_generator

class OutdoorEnvironment(BaseModel):
    source: str
    value: OutdoorEnvironmentValue
    timestamp: datetime

    class Config:
        alias_generator = reverse_alias_generator
