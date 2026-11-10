import os
import sys
import pandas as pd
import warnings

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.pitwall.replay_engine import run_race_replay
from backend.pitwall.validation import run_counterfactual_analysis
from backend.simulation.ml_integration import MLPredictor

def main():
    print("=== Phase 9: Dynamic Pit-Wall Decision Support ===")
    
    # Load ML models safely
    try:
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            predictor = MLPredictor("models/v1")
        print("Successfully loaded real Phase 5 ML Models.")
    except Exception as e:
        print("[ERROR] Phase 5 trained model artifact could not be loaded!")
        sys.exit(1)
        
    print("Loading historical data for replay...")
    df = pd.read_parquet("data/processed/ml_features.parquet")
    
    # Select a race to replay. We'll pick the latest race in the dataset
    latest_race_id = df['raceId'].max()
    df_race = df[df['raceId'] == latest_race_id].copy()
    
    # Select the winning driver of that race for replay evaluation
    df_race_last_lap = df_race.loc[df_race.groupby('driverId')['LapNumber'].idxmax()]
    winner_driver_id = df_race_last_lap.loc[df_race_last_lap['position'].idxmin(), 'driverId']
    
    print(f"\n--- Historical Race Replay ---")
    print(f"Race: {latest_race_id} | Driver: {winner_driver_id}")
    
    # Run Replay Engine. Use mc=100 for acceptable replay speed locally.
    replay_results = run_race_replay(
        df_history=df,
        target_race=latest_race_id,
        target_driver=winner_driver_id,
        start_lap=15, # Start from lap 15 when strategies start evolving
        objective="BALANCED",
        monte_carlo_simulations=100, # Development/Test mode
        predictor=predictor
    )
    
    decision_history = replay_results['decision_history']
    final_decision = replay_results['final_decision']
    
    # Counterfactual Validation
    cf = run_counterfactual_analysis(df, latest_race_id, winner_driver_id, final_decision['strategy'])
    
    print("\n=== Replay Complete ===")
    print(f"Generated {len(decision_history)} dynamic strategy decisions.")
    
    print("\n--- Counterfactual Validation ---")
    print(f"Actual Team Strategy: {cf['actual_strategy']} -> Finished P{cf['actual_finish_position']}")
    print(f"StrategyIQ Recommended: {cf['recommended_strategy']} -> Expected P{final_decision['metrics']['mean_finish_position']:.1f}")
    
    # Reporting
    os.makedirs("reports", exist_ok=True)
    report_md = f"""# Phase 9: Dynamic Pit-Wall Report

## 1. Replay Overview
- **Race ID**: {latest_race_id}
- **Driver ID**: {winner_driver_id}
- **Simulation Compute**: 100 MC Simulations per event

## 2. Decision Log
"""
    for _, row in decision_history.iterrows():
        report_md += f"- **Lap {row['lap']}** [{row['event_trigger']}]: {row['decision']} (Compound: {row['recommended_compound']}, Strategy: {row['strategy']})\n"
        
    report_md += f"""
## 3. Counterfactual Analysis
- **Actual Historical Strategy**: {cf['actual_strategy']} (Finish: P{cf['actual_finish_position']})
- **StrategyIQ Final Recommendation**: {cf['recommended_strategy']} (Expected Finish: P{final_decision['metrics']['mean_finish_position']:.1f})

*Note: The StrategyIQ outcome is a model-based counterfactual under the simulated race conditions.*
"""
    
    with open("reports/phase9_pitwall_report.md", "w") as f:
        f.write(report_md)
        
    # Save History
    os.makedirs("data/processed/pitwall", exist_ok=True)
    decision_history.to_csv("data/processed/pitwall/decision_history.csv", index=False)
    
    print("\nReport saved to reports/phase9_pitwall_report.md")
    
if __name__ == "__main__":
    main()
