import pandas as pd
from typing import Dict, Any

from backend.optimization.objective import ObjectiveWeights, get_weights, CONFIGURATIONS
from backend.optimization.normalization import min_max_normalize
from backend.optimization.risk import extract_risk_metric
from backend.optimization.pareto import identify_pareto_front
from backend.optimization.validation import identify_baseline_strategy

def optimize_strategies(df_monte_carlo: pd.DataFrame, objective_name: str = "BALANCED") -> Dict[str, Any]:
    """
    Core optimizer. Ingests Phase 7 results, normalizes metrics, applies the configured weights,
    calculates Pareto dominance, and returns the mathematically recommended strategy.
    """
    if df_monte_carlo.empty:
        raise ValueError("Phase 7 Monte Carlo results are required before strategy optimization.")
        
    # 1. Weights
    weights = get_weights(objective_name)
    weights.validate()
    
    df = df_monte_carlo.copy()
    
    # 2. Extract and Normalize Risk
    df['Risk'] = extract_risk_metric(df)
    
    # 3. Normalization (1.0 is always best after this step)
    df['Norm_Time'] = min_max_normalize(df['Mean Race Time'], lower_is_better=True)
    df['Norm_Position'] = min_max_normalize(df['Mean Finish Position'], lower_is_better=True)
    df['Norm_Podium'] = min_max_normalize(df['Podium Probability'], lower_is_better=False)
    df['Norm_Win'] = min_max_normalize(df['P1 Probability'], lower_is_better=False)
    df['Norm_Risk'] = min_max_normalize(df['Risk'], lower_is_better=True) # Lower risk penalty is better
    
    # 4. Objective Score Calculation
    df['Objective Score'] = (
        df['Norm_Time'] * weights.race_time +
        df['Norm_Position'] * weights.finish_position +
        df['Norm_Podium'] * weights.podium_probability +
        df['Norm_Win'] * weights.win_probability +
        df['Norm_Risk'] * weights.risk
    )
    
    # 5. Pareto Dominance
    objectives = ['Mean Race Time', 'Mean Finish Position', 'Podium Probability', 'Risk']
    lower_dict = {'Mean Race Time': True, 'Mean Finish Position': True, 'Podium Probability': False, 'Risk': True}
    df['Dominated'] = identify_pareto_front(df, objectives, lower_dict)
    
    # Sort by Score
    df = df.sort_values('Objective Score', ascending=False).reset_index(drop=True)
    
    # 6. Select Winner
    winner = df.iloc[0]
    
    # 7. Baseline Comparison
    baseline_name = identify_baseline_strategy(df)
    baseline = df[df['Strategy'] == baseline_name].iloc[0]
    
    # 8. Human Readable Explanation
    reasoning = [
        f"Strategy '{winner['Strategy']}' achieves the highest {objective_name} objective score ({winner['Objective Score']:.2f}).",
        f"It yields an expected finish of P{winner['Mean Finish Position']:.1f} with a race time of {winner['Mean Race Time']:.1f}s.",
        f"Compared to the baseline ({baseline_name}), it is {baseline['Mean Race Time'] - winner['Mean Race Time']:.1f}s faster expected.",
    ]
    if winner['Dominated']:
        reasoning.append("Warning: This strategy is technically Pareto-dominated in raw metrics, but won due to specific weightings.")
    
    # Return structured dict
    return {
        "recommended_strategy": str(winner['Strategy']),
        "objective": objective_name,
        "score": float(winner['Objective Score']),
        "metrics": {
            "mean_race_time": float(winner['Mean Race Time']),
            "mean_finish_position": float(winner['Mean Finish Position']),
            "p1_probability": float(winner['P1 Probability']),
            "podium_probability": float(winner['Podium Probability']),
            "top5_probability": float(df_monte_carlo.loc[df_monte_carlo['Strategy'] == winner['Strategy'], 'Top-5 Probability'].iloc[0]),
            "risk": float(winner['Risk'])
        },
        "baseline": {
            "strategy": str(baseline_name),
            "time_diff": float(winner['Mean Race Time'] - baseline['Mean Race Time']),
            "pos_diff": float(winner['Mean Finish Position'] - baseline['Mean Finish Position'])
        },
        "reasoning": reasoning,
        "full_results": df.to_dict(orient="records")
    }
