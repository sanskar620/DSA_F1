import pandas as pd
import numpy as np
from typing import List, Dict, Any

def aggregate_monte_carlo_results(mc_results: List[Dict[str, Any]]) -> pd.DataFrame:
    """
    Takes the raw simulation results from multiple strategies and aggregates them.
    Expects mc_results to contain dictionaries from simulate_strategy() output.
    """
    df = pd.DataFrame(mc_results)
    
    # We will group by strategy
    summary_rows = []
    
    for strategy_name, group in df.groupby('strategy_name'):
        total_sims = len(group)
        
        race_times = group['total_predicted_time']
        positions = group['estimated_finish_position']
        
        # Probabilities
        p1_prob = (positions == 1).mean()
        podium_prob = (positions <= 3).mean()
        top5_prob = (positions <= 5).mean()
        top10_prob = (positions <= 10).mean()
        
        summary_rows.append({
            'Strategy': strategy_name,
            'Simulations': total_sims,
            'Stops': group['pit_stops'].iloc[0],
            
            # Time Metrics
            'Mean Race Time': race_times.mean(),
            'Median Race Time': race_times.median(),
            'Std Race Time': race_times.std() if total_sims > 1 else 0.0,
            'Min Race Time': race_times.min(),
            'Max Race Time': race_times.max(),
            '5th Percentile Time': race_times.quantile(0.05),
            '95th Percentile Time': race_times.quantile(0.95),
            
            # Position Metrics
            'Mean Finish Position': positions.mean(),
            'Median Finish Position': positions.median(),
            'Std Finish Position': positions.std() if total_sims > 1 else 0.0,
            'Worst Finish Position': positions.max(),
            
            # Probabilities
            'P1 Probability': p1_prob,
            'Podium Probability': podium_prob,
            'Top-5 Probability': top5_prob,
            'Top-10 Probability': top10_prob,
            
            # Risk (Defined simply as standard deviation of race time here)
            'Risk (Time Std)': race_times.std() if total_sims > 1 else 0.0
        })
        
    return pd.DataFrame(summary_rows).sort_values('Mean Race Time').reset_index(drop=True)
