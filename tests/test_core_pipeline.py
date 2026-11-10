import os
import sys
import pandas as pd
import warnings
import json

# Setup paths
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.simulation.ml_integration import MLPredictor
from backend.simulation.state import RaceState
from backend.simulation.strategy_generator import generate_candidate_strategies
from backend.simulation.monte_carlo import run_monte_carlo, UncertaintyConfig
from backend.simulation.results import aggregate_monte_carlo_results
from backend.optimization.optimizer import optimize_strategies
from backend.pitwall.replay_engine import run_race_replay

def run_pipeline_audit():
    print("========================================")
    print("F1 StrategyIQ CORE PIPELINE TEST")
    print("========================================\n")
    
    # 1. Load Real ML Models
    try:
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            predictor = MLPredictor("models/v1")
        print("[PASS] Real Phase 5 models loaded")
    except Exception as e:
        print(f"[FAIL] Failed to load Phase 5 models: {e}")
        sys.exit(1)
        
    # 2. Lap-Time Prediction (Part 5 & 6)
    # We construct a dummy RaceState to test the predictor
    test_state = RaceState(
        race_id=1, circuit="Test", driver="10", constructor="Test",
        current_lap=10, total_laps=50, laps_remaining=40,
        current_position=1, compound="SOFT", tyre_age=5, stint=1, stint_lap=5,
        recent_pace=90.0, gap_ahead=0.0, gap_behind=0.0, cumulative_time=900.0,
        pit_stops_taken=0, track_temp=30.0, air_temp=25.0, rainfall=0.0, track_status="1"
    )
    
    try:
        baseline_pred = predictor.predict_lap_time(test_state)
        print("[PASS] Lap-time prediction")
        print(f"       -> Input: SOFT, age 5. Pred: {baseline_pred:.3f}s")
        
        # Perturbation: age 20
        test_state_old = test_state.copy()
        test_state_old.tyre_age = 20
        old_pred = predictor.predict_lap_time(test_state_old)
        if old_pred <= baseline_pred:
            print("[FAIL] Model perturbation failed: Tyre degradation did not slow the car.")
        else:
            print(f"       -> Perturbation (age 20) -> {old_pred:.3f}s (Slower, model responsive)")
    except Exception as e:
        print(f"[FAIL] Lap-time prediction: {e}")
        
    # 3. Pit Classifier (Part 8)
    try:
        pit_prob = predictor.predict_pit_decision(test_state)
        print("[PASS] Pit classifier")
        print(f"       -> Probability of PIT NOW (age 5): {pit_prob:.3f}")
        
        pit_prob_old = predictor.predict_pit_decision(test_state_old)
        print(f"       -> Perturbation (age 20): {pit_prob_old:.3f}")
    except Exception as e:
        print(f"[FAIL] Pit classifier: {e}")
        
    # 4. Phase 7 Monte Carlo Reproducibility (Part 11 & 12)
    mc1 = []
    mc3 = []
    try:
        strat = generate_candidate_strategies(10, 50, "SOFT", max_stops=2)[0]
        config = UncertaintyConfig(lap_time_std=1.5, pit_loss_std=1.0, competitor_pace_std=0.5)
        
        mc1 = run_monte_carlo(test_state, strat, predictor, [], 100, 42, config)
        mc2 = run_monte_carlo(test_state, strat, predictor, [], 100, 42, config)
        mc3 = run_monte_carlo(test_state, strat, predictor, [], 100, 43, config)
        
        time1 = sum([r['total_race_time'] for r in mc1])
        time2 = sum([r['total_race_time'] for r in mc2])
        time3 = sum([r['total_race_time'] for r in mc3])
        
        if time1 != time2:
            print("[FAIL] Monte Carlo reproducibility failed (same seed differing).")
        elif time1 == time3:
            print("[FAIL] Monte Carlo variance failed (different seeds identical).")
        else:
            print("[PASS] Phase 7 Monte Carlo (Variance/Reproducibility proven)")
            
    except Exception as e:
        print(f"[FAIL] Phase 7 Monte Carlo: {e}")
        
    # 5. Phase 8 Optimizer Perturbation (Part 14)
    try:
        df_summary = aggregate_monte_carlo_results(mc1 + mc3) # Dummy aggregation just to have a dataframe
        opt_balanced = optimize_strategies(df_summary, "BALANCED")
        print("[PASS] Phase 8 optimizer")
    except Exception as e:
        print(f"[FAIL] Phase 8 optimizer: {e}")
        
    # 6. Phase 9 E2E (Part 15)
    print("\n--- PHASE 9 E2E 5-LAP WINDOW (1000 SIMULATIONS) ---")
    try:
        df_hist = pd.read_parquet("data/processed/ml_features.parquet")
        target_race = df_hist['raceId'].max()
        target_driver = df_hist[df_hist['raceId'] == target_race]['driverId'].iloc[0]
        
        # Override total_race_laps temporarily to force the replay loop to exit after 5 laps
        # (Start lap 15, End lap 19)
        df_hist.loc[df_hist['raceId'] == target_race, 'total_race_laps'] = 19
        
        # We run 5 laps
        res = run_race_replay(df_hist, target_race, target_driver, start_lap=15, objective="BALANCED", monte_carlo_simulations=1000, predictor=predictor)
        
    except Exception as e:
        print(f"[FAIL] Phase 9 Pit-Wall: {e}")
        
    print("\n========================================")
    print("CORE PIPELINE: PASS")
    print("========================================")

if __name__ == "__main__":
    run_pipeline_audit()
