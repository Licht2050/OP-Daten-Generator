from pydantic import BaseModel, Field



class StaffCommunication(BaseModel):
    op_room: str = Field(...)
    sender: str = Field(...)
    message: str = Field(...)
