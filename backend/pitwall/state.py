import pandas as pd
from typing import Dict, Any, List
from backend.simulation.state import RaceState

def reconstruct_leakage_safe_state(df_history: pd.DataFrame, target_race: int, target_driver: int, current_lap: int) -> RaceState:
    """
    Constructs a RaceState object representing the EXACT state of the race at `current_lap`.
    Strictly filters the dataframe to LapNumber <= current_lap to prevent future information leakage.
    """
    # 1. Prevent Leakage
    df_leakage_safe = df_history[(df_history['raceId'] == target_race) & (df_history['LapNumber'] <= current_lap)].copy()
    
    if df_leakage_safe.empty:
        raise ValueError(f"No historical data available for race {target_race} up to lap {current_lap}.")
        
    df_driver = df_leakage_safe[df_leakage_safe['driverId'] == target_driver].copy()
    if df_driver.empty:
        raise ValueError(f"Driver {target_driver} not found or retired before lap {current_lap}.")
        
    # Get the exact state at the target lap
    current_row = df_driver.loc[df_driver['LapNumber'].idxmax()]
    
    # Calculate total laps (can use global max from history since it's a static race property, 
    # but strictly speaking, we use the max lap the leader achieved by the end of the real race.
    # We allow total_race_laps to be known as it is scheduled information).
    total_laps = int(df_history[df_history['raceId'] == target_race]['total_race_laps'].max())
    if pd.isna(total_laps) or total_laps < 1:
        total_laps = 50 # fallback
        
    # Build core state
    state = RaceState(
        race_id=target_race,
        circuit="historical_circuit", # We can map this if needed
        driver=str(target_driver),
        constructor="historical_constructor",
        current_lap=current_lap,
        total_laps=total_laps,
        laps_remaining=total_laps - current_lap,
        current_position=int(current_row.get('position', 1)),
        compound=current_row['compound'],
        tyre_age=int(current_row['tyre_age']),
        stint=int(current_row['Stint']),
        stint_lap=int(current_row['tyre_age']),
        recent_pace=float(current_row.get('recent_pace', 90.0)),
        gap_ahead=0.0, # Could be calculated from cumulative time
        gap_behind=0.0,
        cumulative_time=float(current_row.get('recent_pace', 90.0)) * current_lap, # Approximation for now
        pit_stops_taken=int(current_row['Stint']) - 1,
        track_temp=float(current_row.get('TrackTemp', 30.0)),
        air_temp=float(current_row.get('AirTemp', 25.0)),
        rainfall=float(current_row.get('Rainfall', 0.0)),
        track_status=str(current_row.get('TrackStatus', "1"))
    )
    
    return state

def get_competitor_states(df_history: pd.DataFrame, target_race: int, target_driver: int, current_lap: int) -> List[Dict[str, Any]]:
    """
    Extracts the current state of competitors at the given lap (without leakage).
    """
    df_leakage_safe = df_history[(df_history['raceId'] == target_race) & (df_history['LapNumber'] == current_lap)].copy()
    
    competitors = []
    # Take top 5 competitors for evaluation to save compute
    for _, row in df_leakage_safe.head(6).iterrows():
        if row['driverId'] != target_driver:
            competitors.append({
                'driver': str(row['driverId']),
                'recent_pace': float(row.get('recent_pace', 90.0)),
                'cumulative_time': float(row.get('recent_pace', 90.0)) * current_lap,
                'compound': row['compound'],
                'tyre_age': row['tyre_age'],
                'position': row.get('position', 1)
            })
            
    return competitors[:5]
