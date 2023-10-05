import os
import sys
from pydantic import BaseModel, Field




def reverse_alias_generator(alias: str) -> str:
    mapping = {
        'Operation_Room': 'op_room',
        'Türzustand': 'door_state',
        'Raumtemperatur': 'temperature',
        'Luftfeuchtigkeit': 'humidity',
        'Luftdruck': 'pressure',
        'Beleuchtungsstärke': 'illuminance',
        'CO2_Level': 'co2',
        'Lärmpegel': 'noise',
        'UV-Index': 'uv'
    }
    return mapping.get(alias, alias)

class IndoorEnvironmentDataValue(BaseModel):
    op_room: str = Field(..., alias='Operation_Room')
    door_state: str = Field(..., alias='Türzustand')
    temperature: float = Field(..., alias='Raumtemperatur')
    humidity: float = Field(..., alias='Luftfeuchtigkeit')
    pressure: float = Field(..., alias='Luftdruck')
    illuminance: float = Field(..., alias='Beleuchtungsstärke')
    co2: float = Field(..., alias='CO2_Level')
    noise: float = Field(..., alias='Lärmpegel')
    uv: float = Field(..., alias='UV-Index')

    class Config:
        alias_generator = reverse_alias_generator



class IndoorEnvironmentDataStatus(BaseModel):
    source: str
    value: IndoorEnvironmentDataValue
    timestamp: str

    class Config:
        alias_generator = reverse_alias_generator
