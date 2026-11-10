from pydantic import BaseModel, Field
from typing import Optional

class LapTimeRequest(BaseModel):
    season: int
    race_id: int
    driver_id: int
    lap_number: int = Field(..., ge=1)
    current_position: int = Field(..., ge=1, le=20)
    tyre_age: int = Field(..., ge=0)
    compound: str
    total_laps: Optional[int] = 57
    laps_remaining: Optional[int] = None
    recent_pace: Optional[float] = None
    circuit: Optional[str] = None
    driver: Optional[str] = None
    constructor: Optional[str] = None
    track_temp: Optional[float] = 30.0
    air_temp: Optional[float] = 25.0
    gap_ahead: Optional[float] = 0.0
    gap_behind: Optional[float] = 0.0
    pit_stops_taken: Optional[int] = 1

class LapTimeResponse(BaseModel):
    predicted_lap_time: float
    model: str
    model_version: str

class PitDecisionResponse(BaseModel):
    decision: str
    pit_probability: float
    stay_out_probability: float

class BaseAPIResponse(BaseModel):
    success: bool
    data: Optional[dict] = None
    error: Optional[dict] = None
