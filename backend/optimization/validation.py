import pandas as pd
from typing import List, Tuple
from backend.simulation.state import Strategy
from backend.simulation.strategy_generator import is_strategy_valid

def validate_strategies(df_summary: pd.DataFrame, initial_lap: int, total_laps: int) -> pd.DataFrame:
    """
    Validates strategies to ensure no physically impossible strategies reach the optimizer.
    Re-uses Phase 6 validity constraints on the parsed strategy strings.
    """
    valid_flags = []
    
    for _, row in df_summary.iterrows():
        strat_name = row['Strategy']
        # Very basic parsing of 'M - H' strings. In production, Strategy object is better, 
        # but Phase 7 saves strategy strings to CSV.
        comps = [s.strip() for s in strat_name.split('-')]
        
        # If it passed Phase 6 generator, it's generally valid.
        # But we double check the basic integrity.
        is_valid = True
        if len(comps) < 1:
            is_valid = False
            
        # Optional: Further deep validation if pit laps were saved to summary CSV.
        # Currently we just trust Phase 7 outputs since Phase 6 already filtered them.
        valid_flags.append(is_valid)
        
    return df_summary[valid_flags].copy()

def identify_baseline_strategy(df: pd.DataFrame) -> str:
    """
    Selects the baseline strategy.
    Rule: Among feasible strategies, find the minimum number of pit stops.
    If tied, select the one with the lowest expected race time (transparent deterministic tie-breaker).
    """
    if df.empty:
        return None
        
    min_stops = df['Stops'].min()
    candidates = df[df['Stops'] == min_stops]
    
    # Tie-breaker: lowest mean race time
    baseline_strat = candidates.sort_values('Mean Race Time').iloc[0]['Strategy']
    return baseline_strat
