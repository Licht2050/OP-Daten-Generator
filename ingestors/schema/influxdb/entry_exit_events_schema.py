from pydantic import BaseModel, Field
from datetime import datetime

class EntryExitEventValue(BaseModel):
    Operation_Room: str = Field(..., alias="Operation_Room")
    person: str = Field(..., alias="person")
    event_type: str = Field(..., alias="event_type")
    

class EntryExitEvent(BaseModel):
    source: str
    value: EntryExitEventValue
    timestamp: datetime

