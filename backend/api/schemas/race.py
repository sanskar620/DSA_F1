from pydantic import BaseModel
from typing import Optional, List
from datetime import date

class RaceResponse(BaseModel):
    race_id: int
    season: int
    round: int
    name: str
    circuit: str
    date: date
    total_laps: Optional[int] = 57

class RaceListResponse(BaseModel):
    success: bool
    data: List[RaceResponse]
    error: Optional[str] = None
