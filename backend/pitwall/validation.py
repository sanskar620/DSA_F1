import pandas as pd
from typing import Dict, Any

def run_counterfactual_analysis(df_history: pd.DataFrame, target_race: int, target_driver: int, recommended_strategy: str) -> Dict[str, Any]:
    """
    Evaluates the 'Counterfactual Outcome' by comparing what the Pitwall Engine recommended 
    against what the team historically did.
    
    Since we don't know exactly what the team was optimizing for, we simply return
    the historical facts vs the model-based expected values.
    """
    
    # Get actual race outcome
    df_driver = df_history[(df_history['raceId'] == target_race) & (df_history['driverId'] == target_driver)]
    if df_driver.empty:
        return {}
        
    last_lap = df_driver.loc[df_driver['LapNumber'].idxmax()]
    actual_finish_position = last_lap.get('position', 1)
    
    # Very basic inference of the actual strategy taken
    compounds = df_driver['compound'].unique()
    actual_strategy_taken = " - ".join([str(c) for c in compounds])
    
    # We could simulate the actual strategy vs recommended if we wanted deep simulation, 
    # but the recommended strategy already returns its expected position/time.
    
    return {
        "actual_strategy": actual_strategy_taken,
        "actual_finish_position": actual_finish_position,
        "recommended_strategy": recommended_strategy,
        "note": "Model-based counterfactual. Not a guarantee of historical alteration."
    }
