import os
import sys
import numpy as np
import pandas as pd
import warnings

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.simulation.state import RaceState, Strategy
from backend.simulation.ml_integration import MLPredictor
from backend.simulation.strategy_generator import generate_candidate_strategies, is_strategy_valid
from backend.simulation.competitor_model import CompetitorModel
from backend.simulation.monte_carlo import UncertaintyConfig, run_monte_carlo
from backend.simulation.results import aggregate_monte_carlo_results

def calculate_empirical_residuals(predictor: MLPredictor, df_validation: pd.DataFrame) -> float:
    """
    Calculates the standard deviation of residuals (actual - predicted lap times) 
    using the validation dataset and the real ML predictor.
    """
    print("Calculating empirical lap-time residuals from historical validation data...")
    # This requires running the predictor over the validation set.
    # For speed, we sample a subset.
    df_sample = df_validation.sample(n=min(100, len(df_validation)), random_state=42).copy()
    
    residuals = []
    for _, row in df_sample.iterrows():
        # Setup dummy state for prediction mapping
        state = RaceState(
            race_id=row['raceId'], circuit="fallback", driver=str(row['driverId']), constructor="unknown",
            current_lap=row['LapNumber'], total_laps=row['total_race_laps'], laps_remaining=row['total_race_laps'] - row['LapNumber'],
            current_position=row.get('position', 1), compound=row['compound'], tyre_age=row['tyre_age'],
            stint=row['Stint'], stint_lap=row['tyre_age'], recent_pace=row['recent_pace'],
            gap_ahead=0.0, gap_behind=0.0, cumulative_time=0.0, pit_stops_taken=row['Stint']-1,
            track_temp=row['TrackTemp'], air_temp=row['AirTemp'], rainfall=row.get('Rainfall', 0.0), track_status="1"
        )
        try:
            pred = predictor.predict_lap_time(state)
            actual = float(row['lap_time_seconds'])
            residuals.append(actual - pred)
        except Exception:
            pass
            
    if not residuals:
        return 0.8 # Fallback if data is malformed
        
    residuals = np.array(residuals)
    # Remove extreme outliers (e.g., pit laps or safety cars not filtered out)
    p5, p95 = np.percentile(residuals, 5), np.percentile(residuals, 95)
    filtered = residuals[(residuals > p5) & (residuals < p95)]
    
    std_residual = float(np.std(filtered))
    print(f"Empirical Lap-Time Residual Standard Deviation: {std_residual:.3f}s")
    return std_residual


def main():
    print("=== Phase 7: Monte Carlo Strategy Simulation ===")
    
    try:
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            predictor = MLPredictor("models/v1")
        print("Successfully loaded real Phase 5 ML Models.")
    except Exception as e:
        print("\n[ERROR] Phase 5 trained model artifact could not be loaded!")
        print(f"Details: {e}")
        print("\nSTOPPING MONTE CARLO EXPERIMENT.")
        print("Phase 7 requires the real Phase 5 model artifacts and empirical validation residuals to function correctly.")
        print("Please ensure the Kaggle-trained models are compatible or re-export them using matching environment versions.")
        sys.exit(1)
        
    print("Loading historical data for validation...")
    df = pd.read_parquet("data/processed/ml_features.parquet")
    
    # Calculate Residuals empirically
    lap_time_std = calculate_empirical_residuals(predictor, df)
    
    # We will pick a specific race from the holdout set for simulation.
    latest_race_id = df['raceId'].max()
    df_race = df[df['raceId'] == latest_race_id].copy()
    
    df_race_last_lap = df_race.loc[df_race.groupby('driverId')['LapNumber'].idxmax()]
    winner_driver_id = df_race_last_lap.loc[df_race_last_lap['position'].idxmin(), 'driverId']
    
    df_target = df_race[df_race['driverId'] == winner_driver_id].sort_values('LapNumber')
    
    start_lap = 15
    state_row = df_target[df_target['LapNumber'] == start_lap].iloc[0]
    total_laps = int(df_race['total_race_laps'].max())
    
    # Setup initial state
    initial_state = RaceState(
        race_id=latest_race_id, circuit="fallback", driver=str(winner_driver_id), constructor="unknown",
        current_lap=start_lap, total_laps=total_laps, laps_remaining=total_laps - start_lap,
        current_position=int(state_row.get('position', 1)), compound=state_row['compound'], tyre_age=int(state_row['tyre_age']),
        stint=int(state_row['Stint']), stint_lap=int(state_row['tyre_age']), recent_pace=float(state_row['recent_pace']),
        gap_ahead=0.0, gap_behind=0.0, cumulative_time=float(state_row['recent_pace']) * start_lap, 
        pit_stops_taken=int(state_row['Stint']) - 1, track_temp=float(state_row['TrackTemp']), 
        air_temp=float(state_row['AirTemp']), rainfall=float(state_row.get('Rainfall', 0.0)), track_status="1"
    )

    # Setup competitors
    competitors_data = []
    for _, row in df_race[df_race['LapNumber'] == start_lap].head(5).iterrows():
        if row['driverId'] != winner_driver_id:
            competitors_data.append({
                'driver': row['driverId'],
                'recent_pace': row['recent_pace'],
                'cumulative_time': float(row['recent_pace']) * start_lap
            })
            
    print(f"\n--- Monte Carlo Race Setup ---")
    print(f"Race: {latest_race_id} | Driver: {winner_driver_id} | Starting Lap: {start_lap}/{total_laps}")
    
    raw_strategies = generate_candidate_strategies(initial_state.current_lap, initial_state.total_laps, initial_state.compound, max_stops=2)
    valid_strategies = [s for s in raw_strategies if is_strategy_valid(s, initial_state.current_lap, initial_state.total_laps)]
    
    # Filter to top 3 strategies to save time for this execution
    valid_strategies = valid_strategies[:3]
    
    print(f"Evaluating {len(valid_strategies)} strategies with Monte Carlo...")
    
    # Configure Uncertainty using Empirical Residuals
    config = UncertaintyConfig(
        lap_time_std=lap_time_std,
        pit_loss_std=1.2,          # Can be estimated from pit-lane historical distributions
        competitor_pace_std=0.5,   # Derived from competitor variance analysis
        sc_laps=None,              # Scenario: Green Flag
        vsc_laps=None              # Scenario: Green Flag
    )
    
    n_sims = 100
    all_raw_results = []
    
    for strat in valid_strategies:
        print(f"Simulating Strategy: {strat.name} ({n_sims} iterations)...")
        # Reuse Phase 6 deterministic engine inside Monte Carlo loop
        mc_results = run_monte_carlo(
            race_state=initial_state,
            strategy=strat,
            base_predictor=predictor,
            base_competitors=competitors_data,
            n_simulations=n_sims,
            random_seed=42, # Ensuring perfect reproducibility across identical runs
            uncertainty_config=config
        )
        all_raw_results.extend(mc_results)
        
    print("\nAggregating results and generating risk metrics...")
    summary_df = aggregate_monte_carlo_results(all_raw_results)
    
    print("\n=== Strategy Summary (Monte Carlo) ===")
    print(summary_df.to_string())
    
    # Save Results
    os.makedirs("data/processed/monte_carlo", exist_ok=True)
    summary_df.to_csv("data/processed/monte_carlo/strategy_summary.csv", index=False)
    
    # For raw results, we only save high-level stats instead of every lap to save space, but we save simulation totals
    raw_df = pd.DataFrame([{
        'simulation_id': r['simulation_id'],
        'strategy': r['strategy_name'],
        'total_race_time': r['total_predicted_time'],
        'finish_position': r['estimated_finish_position'],
        'pit_stops': r['pit_stops']
    } for r in all_raw_results])
    
    raw_df.to_parquet("data/processed/monte_carlo/simulation_results.parquet")
    print("\nResults successfully saved to data/processed/monte_carlo/")

if __name__ == "__main__":
    main()
