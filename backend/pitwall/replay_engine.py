import pandas as pd
from typing import Dict, Any

from backend.pitwall.state import reconstruct_leakage_safe_state, get_competitor_states
from backend.pitwall.event_detector import is_meaningful_event
from backend.pitwall.decision_engine import evaluate_pit_decision
from backend.pitwall.history import DecisionHistory
from backend.pitwall.decision_explainer import generate_pit_explanation
from backend.simulation.ml_integration import MLPredictor

def run_race_replay(
    df_history: pd.DataFrame,
    target_race: int,
    target_driver: int,
    start_lap: int,
    objective: str = "BALANCED",
    monte_carlo_simulations: int = 1000,
    predictor: MLPredictor = None
) -> Dict[str, Any]:
    """
    Executes the Historical Race Replay. Loops lap-by-lap, securely reconstructing the race state,
    detecting meaningful events, and orchestrating the Strategy Engine without future leakage.
    """
    
    if predictor is None:
        predictor = MLPredictor("models/v1")
        
    total_laps = int(df_history[df_history['raceId'] == target_race]['total_race_laps'].max())
    
    history_log = DecisionHistory()
    previous_state = None
    
    # Store the final simulated state for counterfactual analysis later
    final_decision = None
    
    for current_lap in range(start_lap, total_laps + 1):
        # 1. Reconstruct exact state
        try:
            current_state = reconstruct_leakage_safe_state(df_history, target_race, target_driver, current_lap)
        except ValueError:
            # Driver retired or data missing
            print(f"Lap {current_lap}: Missing data/Retired. Ending replay.")
            break
            
        # 2. Check for meaningful event
        if is_meaningful_event(current_state, previous_state, df_history):
            event_trigger = "Initial Evaluation" if previous_state is None else "Event Detected/Interval"
            
            # 3. Extract competitors
            competitors = get_competitor_states(df_history, target_race, target_driver, current_lap)
            
            # 4. Run Decision Pipeline
            print(f"--- Lap {current_lap} | Trigger: {event_trigger} ---")
            print("Evaluating Strategy Engine (Running Monte Carlo & Optimizer)...")
            
            decision = evaluate_pit_decision(
                state=current_state,
                competitors=competitors,
                predictor=predictor,
                objective=objective,
                mc_sims=monte_carlo_simulations
            )
            
            # 5. Log and Explain
            history_log.add_decision(current_lap, event_trigger, decision)
            explanation = generate_pit_explanation(decision)
            
            print(explanation)
            print("-" * 50)
            
            final_decision = decision
            
        previous_state = current_state
        
    return {
        "race_id": target_race,
        "driver_id": target_driver,
        "decision_history": history_log.to_dataframe(),
        "final_decision": final_decision
    }
