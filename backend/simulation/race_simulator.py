from typing import List, Dict, Any, Callable
import pandas as pd
from backend.simulation.state import RaceState, Strategy
from backend.simulation.ml_integration import MLPredictor
from backend.simulation.competitor_model import CompetitorModel
from backend.simulation.pit_loss import get_pit_loss

def simulate_strategy(
    strategy: Strategy, 
    initial_state: RaceState, 
    predictor: MLPredictor, 
    competitors: CompetitorModel,
    pit_loss_func: Callable[[str], float] = get_pit_loss
) -> Dict[str, Any]:
    """
    Simulates a race deterministically lap-by-lap for a given strategy.
    """
    state = initial_state.copy()
    lap_history = []
    
    # We maintain a separate competitor model per simulation branch
    import copy
    comp_model = copy.deepcopy(competitors)
    
    for _ in range(state.current_lap, state.total_laps):
        lap_dict = {}
        lap_dict['lap'] = state.current_lap
        
        # 1. Check for pit stop
        pit_stop_taken = False
        if state.current_lap in strategy.pit_laps:
            pit_stop_taken = True
            pit_loss = pit_loss_func(state.circuit)
            state.cumulative_time += pit_loss
            state.pit_stops_taken += 1
            
            # Change compound based on strategy plan
            pit_idx = strategy.pit_laps.index(state.current_lap)
            # The next compound is at pit_idx + 1 in planned_compounds
            if pit_idx + 1 < len(strategy.planned_compounds):
                state.compound = strategy.planned_compounds[pit_idx + 1]
                
            state.tyre_age = 0
            state.stint += 1
            state.stint_lap = 1
        
        # Now capture state for the history after potential pit modifications
        lap_dict['compound'] = state.compound
        lap_dict['tyre_age'] = state.tyre_age
        lap_dict['stint_number'] = state.stint
        lap_dict['pit_stop'] = pit_stop_taken
        
        # 2. Predict Lap Time (ML Model 1)
        # Model 1 handles the combined degradation and fuel-burn effects automatically
        predicted_time = predictor.predict_lap_time(state)
        lap_dict['predicted_lap_time'] = predicted_time
        
        # Update State Time
        state.cumulative_time += predicted_time
        lap_dict['cumulative_time'] = state.cumulative_time
        
        # 3. Competitor and Position Estimation
        comp_model.simulate_lap()
        est_position = comp_model.get_estimated_position(state.cumulative_time)
        lap_dict['estimated_position'] = est_position
        
        # Save historical record
        lap_history.append(lap_dict)
        
        # 4. Advance State to next lap
        state.current_lap += 1
        state.laps_remaining -= 1
        state.tyre_age += 1
        state.stint_lap += 1
        
        # Update recent pace (smoothing function mimicking a rolling average)
        # 80% old recent pace, 20% new lap time
        state.recent_pace = (state.recent_pace * 0.8) + (predicted_time * 0.2)
        
    return {
        "strategy_name": strategy.name,
        "pit_laps": strategy.pit_laps,
        "total_predicted_time": state.cumulative_time,
        "estimated_finish_position": est_position,
        "pit_stops": state.pit_stops_taken,
        "lap_history": lap_history
    }

def compare_strategies(
    strategies: List[Strategy], 
    initial_state: RaceState, 
    predictor: MLPredictor, 
    competitors: CompetitorModel
) -> pd.DataFrame:
    """
    Simulates all valid candidate strategies and returns a comparison DataFrame.
    """
    results = []
    import pandas as pd
    
    for strat in strategies:
        sim_result = simulate_strategy(strat, initial_state, predictor, competitors)
        results.append({
            "Strategy": sim_result["strategy_name"],
            "Stops": sim_result["pit_stops"],
            "Predicted Time": sim_result["total_predicted_time"],
            "Estimated Position": sim_result["estimated_finish_position"]
        })
        
    df_results = pd.DataFrame(results)
    # Sort by lowest predicted race time
    return df_results.sort_values(by="Predicted Time").reset_index(drop=True)
