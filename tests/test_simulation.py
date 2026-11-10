import pytest
from backend.simulation.state import RaceState, Strategy
from backend.simulation.strategy_generator import generate_candidate_strategies, is_strategy_valid
from backend.simulation.competitor_model import CompetitorModel

# Dummy Mock Predictor for testing without loading ML models
class MockPredictor:
    def predict_lap_time(self, state: RaceState) -> float:
        # Base pace 90 seconds, add tyre age penalty, subtract fuel burn
        fuel_burn = (state.current_lap / max(state.total_laps, 1)) * 2.0
        tyre_deg = state.tyre_age * 0.1
        return 90.0 + tyre_deg - fuel_burn

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

def test_strategy_generation():
    strategies = generate_candidate_strategies(10, 50, "MEDIUM", max_stops=1)
    assert len(strategies) > 0
    # Check if a 1-stop strategy has exactly 1 pit lap
    strat = strategies[0]
    assert len(strat.pit_laps) == 1
    assert len(strat.planned_compounds) == 2

def test_invalid_strategy_rejection():
    # Pit lap before current lap
    bad_strat = Strategy("Bad", "MEDIUM", ["MEDIUM", "HARD"], [5])
    assert not is_strategy_valid(bad_strat, current_lap=10, total_laps=50)
    
    # Pit lap after race end
    bad_strat_2 = Strategy("Bad", "MEDIUM", ["MEDIUM", "HARD"], [55])
    assert not is_strategy_valid(bad_strat_2, current_lap=10, total_laps=50)

def test_deterministic_simulation():
    from backend.simulation.race_simulator import simulate_strategy
    
    state = get_test_state()
    strat = Strategy("M-H", "MEDIUM", ["MEDIUM", "HARD"], [25])
    comp_model = CompetitorModel([{'driver': 'BOT', 'cumulative_time': 905.0, 'recent_pace': 90.5}])
    predictor = MockPredictor()
    
    res1 = simulate_strategy(strat, state, predictor, comp_model)
    res2 = simulate_strategy(strat, state, predictor, comp_model)
    
    assert res1["total_predicted_time"] == res2["total_predicted_time"]
    assert res1["pit_stops"] == 1
    assert res1["estimated_finish_position"] == res2["estimated_finish_position"]

def test_tyre_age_reset_on_pit():
    from backend.simulation.race_simulator import simulate_strategy
    
    state = get_test_state()
    strat = Strategy("M-H", "MEDIUM", ["MEDIUM", "HARD"], [11]) # pit immediately next lap
    comp_model = CompetitorModel([])
    predictor = MockPredictor()
    
    res = simulate_strategy(strat, state, predictor, comp_model)
    history = res["lap_history"]
    
    # Lap 10 was age 10
    # Lap 11 is pit lap (pit happens, age goes to 0, then at end of lap age increments to 1)
    # Wait, the simulator adds age at the end of the lap.
    
    lap_11_state = next(l for l in history if l['lap'] == 11)
    assert lap_11_state['pit_stop'] is True
    # In simulator: tyre_age is 0 during prediction, then becomes 1 at end.
    # The history dictionary captures it BEFORE the end-of-lap increment.
    assert lap_11_state['tyre_age'] == 0
    assert lap_11_state['stint_number'] == 2
    assert lap_11_state['compound'] == 'HARD'
