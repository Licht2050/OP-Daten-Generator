from pydantic import BaseModel, Field
from typing import Dict, List, Optional, Union

def reverse_alias_generator(alias: str) -> str:
    mapping = {
        'Straße': 'street',
        'Stadt': 'city',
        'Postleitzahl': 'postal_code',
        'Vorerkrankung': 'illness',
        'Diagnosedatum': 'diagnosis_date',
        'Behandlung': 'treatment',
        'Behandlungsdatum': 'treatment_date',
        'Weitere Informationen': 'additional_info',
        'Urlaubsort': 'destination',
        'Aktivitaet': 'activity',
        'Dauer': 'duration',
        'Startdatum': 'start_date',
        'Enddatum': 'end_date',
        'Patient_ID': 'patient_id',
        'Vorname': 'first_name',
        'Name': 'last_name',
        'Geschlecht': 'gender',
        'Geburtsdatum': 'birthdate',
        'Blutgruppe': 'blood_group',
        'Gewicht': 'weight',
        'Größe': 'height'
    }
    return mapping.get(alias, alias)

class Address(BaseModel):
    street: str = Field(..., alias='Straße')
    city: str = Field(..., alias='Stadt')
    postal_code: int = Field(..., alias='Postleitzahl')
    
    class Config:
        alias_generator = reverse_alias_generator

class IllnessRecord(BaseModel):
    illness: str = Field(..., alias='Vorerkrankung')
    diagnosis_date: str = Field(..., alias='Diagnosedatum')
    treatment: str = Field(..., alias='Behandlung')
    treatment_date: str = Field(..., alias='Behandlungsdatum')
    additional_info: Optional[str] = Field(None, alias='Weitere Informationen')

    class Config:
        alias_generator = reverse_alias_generator

class HolidayRecord(BaseModel):
    destination: str = Field(..., alias='Urlaubsort')
    activity: str = Field(..., alias='Aktivitaet')
    duration: int = Field(..., alias='Dauer')
    start_date: str = Field(..., alias='Startdatum')
    end_date: str = Field(..., alias='Enddatum')
    
    class Config:
        alias_generator = reverse_alias_generator

class OperationTeam(BaseModel):
    doctors: List[str] = Field(default_factory=list)
    nurses: List[str] = Field(default_factory=list)
    anesthetists: List[str] = Field(default_factory=list)

class Patient(BaseModel):
    patient_id: str = Field(..., alias='Patient_ID')
    first_name: Optional[str] = Field(None, alias='Vorname')
    last_name: Optional[str] = Field(None, alias='Name')
    gender: Optional[str] = Field(None, alias='Geschlecht')
    birthdate: Optional[str] = Field(None, alias='Geburtsdatum')
    blood_group: Optional[str] = Field(None, alias='Blutgruppe')
    weight: Optional[Union[int, None]] = Field(None, alias='Gewicht')
    height: Optional[Union[int, None]] = Field(None, alias='Größe')
    address: Optional[Address] = Field(None)
    illness_records: List[IllnessRecord] = Field(default_factory=list)
    holiday_records: List[HolidayRecord] = Field(default_factory=list)
    op_team: Optional[OperationTeam] = Field(None)
    
    class Config:
        alias_generator = reverse_alias_generator

