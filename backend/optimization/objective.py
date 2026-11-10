from dataclasses import dataclass
from typing import Dict

@dataclass
class ObjectiveWeights:
    race_time: float
    finish_position: float
    podium_probability: float
    win_probability: float
    risk: float

    def validate(self):
        """Ensures weights are numeric, non-negative, and sum to 1.0."""
        weights = [self.race_time, self.finish_position, self.podium_probability, self.win_probability, self.risk]
        
        if any(not isinstance(w, (int, float)) for w in weights):
            raise ValueError("All weights must be numeric.")
        
        if any(w < 0 for w in weights):
            raise ValueError("All weights must be non-negative.")
            
        total = sum(weights)
        if abs(total - 1.0) > 1e-5:
            raise ValueError(f"Weights must sum to 1.0. Current sum: {total}")

# Standard predefined configurations. 
# These are decision preferences, NOT universally correct definitions of optimality.
CONFIGURATIONS: Dict[str, ObjectiveWeights] = {
    "RACE_TIME": ObjectiveWeights(
        race_time=1.0, finish_position=0.0, podium_probability=0.0, win_probability=0.0, risk=0.0
    ),
    "FINISH_POSITION": ObjectiveWeights(
        race_time=0.0, finish_position=1.0, podium_probability=0.0, win_probability=0.0, risk=0.0
    ),
    "PODIUM": ObjectiveWeights(
        race_time=0.1, finish_position=0.3, podium_probability=0.6, win_probability=0.0, risk=0.0
    ),
    "RISK_AWARE": ObjectiveWeights(
        race_time=0.25, finish_position=0.25, podium_probability=0.20, win_probability=0.0, risk=0.30
    ),
    "BALANCED": ObjectiveWeights(
        race_time=0.25, finish_position=0.30, podium_probability=0.25, win_probability=0.10, risk=0.10
    )
}

def get_weights(objective_name: str) -> ObjectiveWeights:
    name = objective_name.upper()
    synonyms = {
        "CONSERVATIVE": "RISK_AWARE",
        "AGGRESSIVE": "PODIUM",
        "SAFE": "RISK_AWARE",
        "ATTACK": "PODIUM"
    }
    target = synonyms.get(name, name)
    if target not in CONFIGURATIONS:
        target = "BALANCED"
    return CONFIGURATIONS[target]
