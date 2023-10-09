from pydantic import BaseModel, Field, root_validator
from typing import Dict, List, Optional, Union
from datetime import datetime

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
        'Größe': 'height',
        'Operation_Type': 'operation_type',
        'Operation_Room': 'operation_room',
        'Duration': 'duration',
        'Date': 'operation_date',
        'Anaesthesia_Type': 'anesthesia_typ',
        'Medical_Devices': 'medical_devices',
        'Operation_Outcome': 'operation_outcome',

    }
    return mapping.get(alias, alias)

class Address(BaseModel):
    street: str = Field(default=None, alias='Straße')
    city: str = Field(default=None, alias='Stadt')
    postal_code: int = Field(default=None, alias='Postleitzahl')
    
    class Config:
        alias_generator = reverse_alias_generator

    @root_validator(pre=True)
    def check_fields(cls, values):
        if all(value is None for value in values.values()):
            raise ValueError("All fields are None")
        return values

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
    patient_id: str = Field(..., alias='Patient_ID')
    doctors: List[str] = Field(default_factory=list)
    nurses: List[str] = Field(default_factory=list)
    anesthetists: List[str] = Field(default_factory=list)


class PreOPRecord(BaseModel):
    operation_type: str = Field(..., alias='Operation_Type')
    operation_room: str = Field(..., alias='Operation_Room')
    duration: int = Field(..., alias='Duration', description="Dauer der Operation in Minuten")
    operation_date: datetime = Field(..., alias='Date')
    anesthesia_typ : str = Field(..., alias='Anaesthesia_Type')    
    medical_devices: List[str] = Field(default_factory=list, alias='Medical_Devices')


    class Config:
        alias_generator = reverse_alias_generator

class PostOPRecord(BaseModel):
    
    operation_outcome: str = Field(..., alias='Operation_Outcome')
    notes: Optional[str] = Field(None, alias='Notes')


    class Config:
        alias_generator = reverse_alias_generator

class OpDetails(BaseModel):
    patient_id: str = Field(..., alias='Patient_ID')
    pre_op_record: Optional[PreOPRecord] = Field(None, alias='Pre_OP_Record')
    post_op_record: Optional[PostOPRecord] = Field(None, alias='Post_OP_Record')
    op_team: Optional[OperationTeam] = Field(None)

    class Config:
        alias_generator = reverse_alias_generator




class Patient(BaseModel):
    patient_id: str = Field(..., alias='Patient_ID', description="Einzigartige ID zur Identifizierung des Patienten")
    first_name: Optional[str] = Field(None, alias='Vorname', description="Vorname des Patienten", min_length=1, max_length=100)
    last_name: Optional[str] = Field(default=None, alias='Name', description="Nachname des Patienten", min_length=1, max_length=100)
    gender: Optional[str] = Field(None, alias='Geschlecht', description="Geschlecht des Patienten")
    birthdate: Optional[str] = Field(None, alias='Geburtsdatum', description="Geburtsdatum des Patienten")
    blood_group: Optional[str] = Field(None, alias='Blutgruppe', description="Blutgruppe des Patienten")
    weight: Optional[Union[int, None]] = Field(None, alias='Gewicht', description="Gewicht des Patienten in kg") 
    height: Optional[Union[int, None]] = Field(None, alias='Größe', description="Größe des Patienten in cm")
    address: Optional[Address] = Field(None)
    illness_records: List[IllnessRecord] = Field(default_factory=list)
    # holiday_records: List[HolidayRecord] = Field(default_factory=list)
    # op_team: Optional[OperationTeam] = Field(None)
    # operation_records: Optional[OperationRecord] = Field(None, alias='Operation_Record')


    class Config:
        alias_generator = reverse_alias_generator

