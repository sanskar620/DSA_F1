from pydantic import BaseModel, Field
from typing import Optional, List
from backend.api.schemas.strategy import RaceStateSchema

class PitWallDecisionRequest(BaseModel):
    race_state: RaceStateSchema
    objective: str = "BALANCED"
    simulation_count: int = Field(1000, ge=1, le=1000)

class ReplayRequest(BaseModel):
    race_id: int
    driver_id: int
    start_lap: int = Field(..., ge=1)
    end_lap: int = Field(..., ge=1)
    objective: str = "BALANCED"
    simulation_count: int = Field(1000, ge=1, le=1000)
