import pytest
import numpy as np
from backend.simulation.state import RaceState, Strategy
from backend.simulation.monte_carlo import UncertaintyConfig, run_monte_carlo
from backend.simulation.results import aggregate_monte_carlo_results

# Simple predictable mock for unit testing ONLY
class TestMockPredictor:
    def predict_lap_time(self, state: RaceState) -> float:
        return 90.0

def get_test_state():
    return RaceState(
        race_id=1, circuit="test", driver="TST", constructor="TEST",
        current_lap=10, total_laps=50, laps_remaining=40,
        current_position=1, compound="MEDIUM", tyre_age=10,
        stint=1, stint_lap=10, recent_pace=90.0,
        gap_ahead=0.0, gap_behind=5.0, cumulative_time=900.0,
        pit_stops_taken=0, track_temp=30.0, air_temp=25.0,
        rainfall=0.0, track_status="1"
    )

def test_monte_carlo_reproducibility():
    """Test that running with the same seed yields identical raw results."""
    state = get_test_state()
    strat = Strategy("M", "MEDIUM", ["MEDIUM"], [])
    predictor = TestMockPredictor()
    comps = [{'driver': 'BOT', 'cumulative_time': 905.0, 'recent_pace': 90.5}]
    
    config = UncertaintyConfig(lap_time_std=1.0)
    
    res1 = run_monte_carlo(state, strat, predictor, comps, n_simulations=10, random_seed=42, uncertainty_config=config)
    res2 = run_monte_carlo(state, strat, predictor, comps, n_simulations=10, random_seed=42, uncertainty_config=config)
    
    for r1, r2 in zip(res1, res2):
        assert r1['total_predicted_time'] == r2['total_predicted_time']
        
def test_monte_carlo_stochasticity():
    """Test that running with different seeds yields different stochastic results."""
    state = get_test_state()
    strat = Strategy("M", "MEDIUM", ["MEDIUM"], [])
    predictor = TestMockPredictor()
    comps = [{'driver': 'BOT', 'cumulative_time': 905.0, 'recent_pace': 90.5}]
    
    config = UncertaintyConfig(lap_time_std=1.0)
    
    res1 = run_monte_carlo(state, strat, predictor, comps, n_simulations=10, random_seed=42, uncertainty_config=config)
    res2 = run_monte_carlo(state, strat, predictor, comps, n_simulations=10, random_seed=99, uncertainty_config=config)
    
    # Very likely they are not exactly equal due to different noise
    assert any(r1['total_predicted_time'] != r2['total_predicted_time'] for r1, r2 in zip(res1, res2))

def test_aggregation_metrics():
    """Test that probabilities remain between 0 and 1, and calculations are valid."""
    mc_results = [
        {'simulation_id': 0, 'strategy_name': 'M', 'pit_stops': 1, 'total_predicted_time': 1000.0, 'estimated_finish_position': 1},
        {'simulation_id': 1, 'strategy_name': 'M', 'pit_stops': 1, 'total_predicted_time': 1005.0, 'estimated_finish_position': 2},
        {'simulation_id': 2, 'strategy_name': 'M', 'pit_stops': 1, 'total_predicted_time': 1010.0, 'estimated_finish_position': 4},
        {'simulation_id': 3, 'strategy_name': 'M', 'pit_stops': 1, 'total_predicted_time': 1015.0, 'estimated_finish_position': 10},
    ]
    
    df = aggregate_monte_carlo_results(mc_results)
    
    assert len(df) == 1
    row = df.iloc[0]
    assert row['Simulations'] == 4
    assert row['Mean Race Time'] == 1007.5
    assert row['P1 Probability'] == 0.25      # 1 out of 4
    assert row['Podium Probability'] == 0.50  # Pos 1 and 2
    assert row['Top-5 Probability'] == 0.75   # Pos 1, 2, 4
    assert row['Top-10 Probability'] == 1.0   # Pos 1, 2, 4, 10
