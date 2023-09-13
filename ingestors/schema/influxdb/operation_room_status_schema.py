import os
import sys
from pydantic import BaseModel, Field
from typing import Dict, Union



def reverse_alias_generator(alias: str) -> str:
    mapping = {
        'Operation_Room': 'Operation_Room',
        'Türzustand': 'door_state',
        'Raumtemperatur': 'room_temperature',
        'Luftfeuchtigkeit': 'air_humidity',
        'Luftdruck': 'air_pressure',
        'Beleuchtungsstärke': 'illumination_intensity',
    }
    return mapping.get(alias, alias)

class OperationRoomStatusValue(BaseModel):
    Operation_Room: str = Field(..., alias='Operation_Room')
    door_state: str = Field(..., alias='Türzustand')
    room_temperature: float = Field(..., alias='Raumtemperatur')
    air_humidity: float = Field(..., alias='Luftfeuchtigkeit')
    air_pressure: float = Field(..., alias='Luftdruck')
    illumination_intensity: float = Field(..., alias='Beleuchtungsstärke')

    class Config:
        alias_generator = reverse_alias_generator

class OperationRoomStatus(BaseModel):
    source: str
    value: OperationRoomStatusValue
    timestamp: str

    class Config:
        alias_generator = reverse_alias_generator
