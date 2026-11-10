import pandas as pd
from typing import Dict, List, Any
from backend.optimization.objective import CONFIGURATIONS
from backend.optimization.optimizer import optimize_strategies

def run_sensitivity_analysis(df_monte_carlo: pd.DataFrame) -> Dict[str, Any]:
    """
    Evaluates how the recommended strategy changes when exposed to different 
    objective configurations. This determines the recommendation's robustness.
    """
    results = {}
    winning_strategies = []
    
    for obj_name in CONFIGURATIONS.keys():
        opt_res = optimize_strategies(df_monte_carlo, objective_name=obj_name)
        strat = opt_res['recommended_strategy']
        results[obj_name] = strat
        winning_strategies.append(strat)
        
    primary_winner = results.get('BALANCED')
    
    # Calculate how many configurations picked the primary winner
    robustness_count = winning_strategies.count(primary_winner)
    
    if robustness_count >= len(CONFIGURATIONS) - 1:
        confidence = "HIGH (Robust across almost all tested objectives)"
    elif robustness_count >= 2:
        confidence = "MEDIUM (Sensitive to specific extreme weightings)"
    else:
        confidence = "LOW (Highly sensitive to objective definition)"
        
    return {
        "primary_recommendation": primary_winner,
        "recommendation_robustness": confidence,
        "sensitivity_map": results
    }
