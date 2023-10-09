from pydantic import BaseModel, Field
from datetime import datetime



class EntryExitEventValue(BaseModel):
    op_room: str = Field(..., alias="op_room")
    person: str = Field(..., alias="person")
    event: str = Field(..., alias="event")
    



class EntryExitEvent(BaseModel):
    source: str
    value: EntryExitEventValue
    timestamp: datetime

