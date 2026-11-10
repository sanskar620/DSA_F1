from typing import List
from backend.simulation.state import Strategy

def generate_candidate_strategies(
    current_lap: int,
    total_laps: int,
    current_compound: str,
    available_compounds: List[str] = ["SOFT", "MEDIUM", "HARD"],
    max_stops: int = 2
) -> List[Strategy]:
    """
    Generates realistic candidate strategies based on current state.
    """
    strategies = []
    laps_remaining = total_laps - current_lap
    
    if laps_remaining <= 0:
        return strategies

    # Filter out compounds that don't make sense (e.g. wet tyres if it's dry, but we'll stick to basic dry for now)
    compounds = [c for c in available_compounds if c in ["SOFT", "MEDIUM", "HARD"]]
    
    # 1-Stop Strategies
    if max_stops >= 1 and laps_remaining > 5:
        for c in compounds:
            # We don't want to pit for the exact same compound in a 1-stop usually, but sometimes teams do.
            # Let's generate a pit window roughly in the middle of the remaining race.
            pit_lap = current_lap + int(laps_remaining * 0.5)
            strat = Strategy(
                name=f"{current_compound} - {c}",
                starting_compound=current_compound,
                planned_compounds=[current_compound, c],
                pit_laps=[pit_lap]
            )
            strategies.append(strat)
            
    # 2-Stop Strategies
    if max_stops >= 2 and laps_remaining > 20:
        for c1 in compounds:
            for c2 in compounds:
                pit1 = current_lap + int(laps_remaining * 0.33)
                pit2 = current_lap + int(laps_remaining * 0.66)
                strat = Strategy(
                    name=f"{current_compound} - {c1} - {c2}",
                    starting_compound=current_compound,
                    planned_compounds=[current_compound, c1, c2],
                    pit_laps=[pit1, pit2]
                )
                strategies.append(strat)

    return strategies

def is_strategy_valid(strategy: Strategy, current_lap: int, total_laps: int) -> bool:
    """Basic validation rules for a generated strategy."""
    if not strategy.pit_laps:
        return True # 0-stop is technically valid for sprint races or finishing a race
    
    # Pits must be strictly increasing and within bounds
    prev_pit = current_lap
    for pit in strategy.pit_laps:
        if pit <= prev_pit:
            return False
        if pit >= total_laps:
            return False
        prev_pit = pit
        
    if len(strategy.planned_compounds) != len(strategy.pit_laps) + 1:
        return False
        
    return True
