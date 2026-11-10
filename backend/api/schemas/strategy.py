from pydantic import BaseModel, Field
from typing import List, Optional

class RaceStateSchema(BaseModel):
    race_id: int
    circuit: str
    driver: str
    constructor: str
    driver_id: Optional[int] = 1
    season: Optional[int] = 2024
    current_lap: int = Field(..., ge=1)
    total_laps: int
    laps_remaining: int
    current_position: int = Field(..., ge=1, le=20)
    compound: str
    tyre_age: int = Field(..., ge=0)
    stint: int
    stint_lap: int
    recent_pace: float
    gap_ahead: float
    gap_behind: float
    cumulative_time: float
    pit_stops_taken: int
    track_temp: float
    air_temp: float
    rainfall: float
    track_status: str

class StrategySchema(BaseModel):
    name: str
    starting_compound: str
    planned_compounds: List[str]
    pit_laps: List[int]

class SimulateRequest(BaseModel):
    race_state: RaceStateSchema
    strategy: StrategySchema

class MonteCarloRequest(BaseModel):
    race_state: RaceStateSchema
    strategy: StrategySchema
    simulation_count: int = Field(1000, ge=1, le=1000)
    random_seed: int = 42

class OptimizeRequest(BaseModel):
    race_state: RaceStateSchema
    candidate_strategies: List[StrategySchema]
    objective: str = "BALANCED"
    simulation_count: int = Field(1000, ge=1, le=1000)
