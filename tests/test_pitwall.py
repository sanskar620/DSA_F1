import pytest
import pandas as pd
from backend.pitwall.state import reconstruct_leakage_safe_state
from backend.pitwall.event_detector import is_meaningful_event
from backend.simulation.state import RaceState

def get_dummy_history():
    return pd.DataFrame({
        'raceId': [1, 1, 1],
        'driverId': [10, 10, 10],
        'LapNumber': [1, 2, 3],
        'position': [1, 1, 2],
        'compound': ['SOFT', 'SOFT', 'SOFT'],
        'tyre_age': [1, 2, 3],
        'Stint': [1, 1, 1],
        'recent_pace': [90.0, 91.0, 92.0],
        'total_race_laps': [50, 50, 50]
    })
    
def test_leakage_prevention():
    df = get_dummy_history()
    
    # Reconstruct state at Lap 2. It should NOT know position=2 at Lap 3.
    state = reconstruct_leakage_safe_state(df, target_race=1, target_driver=10, current_lap=2)
    
    assert state.current_lap == 2
    assert state.current_position == 1 # Accurate to lap 2
    assert state.tyre_age == 2
    
def test_event_detector():
    s1 = RaceState(1,"c","d","c",10,50,40,1,"M",10,1,10,90,0,0,900,0,30,25,0,"1")
    s2 = RaceState(1,"c","d","c",15,50,35,1,"M",15,1,15,90,0,0,1350,0,30,25,0,"1")
    
    # 5 laps passed -> True
    assert is_meaningful_event(s2, s1, None) == True
    
    s3 = RaceState(1,"c","d","c",11,50,39,1,"M",11,1,11,90,0,0,990,0,30,25,0,"4") # SC
    
    # SC deployed -> True
    assert is_meaningful_event(s3, s1, None) == True
    
    s4 = RaceState(1,"c","d","c",11,50,39,1,"M",11,1,11,90,0,0,990,0,30,25,0,"1") # 1 lap, no change
    # Nothing changed -> False
    assert is_meaningful_event(s4, s1, None) == False
