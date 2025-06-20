from pydantic import BaseModel, Field
from typing import Optional, Union
from datetime import datetime

class PredictiveMaintenanceSchema(BaseModel):
    datetime: datetime
    machineID: str
    model: str
    volt: float = Field(ge=0)
    rotate: float = Field(ge=0)
    pressure: float = Field(ge=0)
    vibration: float = Field(ge=0)
    age: float = Field(ge=0)
    errorID: str
    failure: str
    comp_maint: str

    class Config:
        extra = "forbid"  # Reject any extra fields 