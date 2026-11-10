from dataclasses import dataclass, field
from typing import List, Dict, Optional

@dataclass
class Strategy:
    """Represents a planned race strategy."""
    name: str
    starting_compound: str
    planned_compounds: List[str]  # e.g., ["MEDIUM", "HARD"]
    pit_laps: List[int]           # e.g., [35]

@dataclass
class RaceState:
    """Represents the deterministic state of the race at a given lap."""
    race_id: int
    circuit: str
    driver: str
    constructor: str
    
    current_lap: int
    total_laps: int
    laps_remaining: int
    
    current_position: int
    compound: str
    tyre_age: int
    stint: int
    stint_lap: int
    
    recent_pace: float
    gap_ahead: float
    gap_behind: float
    
    cumulative_time: float
    pit_stops_taken: int
    
    # Weather & Track (kept constant for Phase 6 deterministic sim unless updated)
    track_temp: float
    air_temp: float
    rainfall: float
    track_status: str
    
    def copy(self):
        """Creates a deep copy of the state for simulation branching."""
        import copy
        return copy.deepcopy(self)
