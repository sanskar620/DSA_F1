from backend.simulation.state import RaceState
import pandas as pd

def is_meaningful_event(current_state: RaceState, previous_state: RaceState, df_history: pd.DataFrame) -> bool:
    """
    Determines if a meaningful event has occurred that justifies burning compute 
    to re-run the 1000 Monte Carlo simulations.
    """
    if previous_state is None:
        return True # Initial evaluation
        
    # 1. Race Control Changes (Safety Car, VSC)
    if current_state.track_status != previous_state.track_status:
        # e.g. Green to SC, or SC to Green
        return True
        
    # 2. Weather Changes
    if current_state.rainfall != previous_state.rainfall:
        return True
        
    # 3. Time-based evaluation
    # Even if nothing happened, re-evaluate every 5 laps to ensure strategy is tracking optimally.
    if current_state.current_lap - previous_state.current_lap >= 5:
        return True
        
    # 4. Critical Tyre Age Reached
    # Softs degrade fast, Hards slow. If tyre age crosses a threshold.
    if current_state.tyre_age >= 15 and current_state.tyre_age % 3 == 0:
        return True
        
    # Note: A real implementation would also detect if a direct competitor pitted on this lap.
    # For now, this strict list prevents running 50 evaluations.
    return False
