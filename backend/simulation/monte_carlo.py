import copy
import numpy as np
from typing import List, Dict, Any, Optional
from dataclasses import dataclass

from backend.simulation.state import RaceState, Strategy
from backend.simulation.ml_integration import MLPredictor
from backend.simulation.competitor_model import CompetitorModel
from backend.simulation.race_simulator import simulate_strategy

@dataclass
class UncertaintyConfig:
    """
    Configuration for Monte Carlo Uncertainty.
    All sigmas (std devs) should be derived from historical/empirical data.
    """
    lap_time_std: float = 0.0
    pit_loss_std: float = 0.0
    competitor_pace_std: float = 0.0
    # Additional scenario variables could go here (e.g. SC laps)
    sc_laps: List[int] = None
    vsc_laps: List[int] = None

class StochasticPredictor(MLPredictor):
    """
    Wraps the real MLPredictor. Adds empirical random noise to the predicted lap time.
    """
    def __init__(self, base_predictor: MLPredictor, config: UncertaintyConfig, rng: np.random.Generator):
        self.base_predictor = base_predictor
        self.config = config
        self.rng = rng

    def predict_lap_time(self, state: RaceState) -> float:
        # Get true deterministic prediction from Kaggle model
        base_time = self.base_predictor.predict_lap_time(state)
        
        # Inject realistic uncertainty
        noise = self.rng.normal(0, self.config.lap_time_std)
        
        # Safety Cars and VSC scenarios (if enabled) greatly slow the pace
        if self.config.sc_laps and state.current_lap in self.config.sc_laps:
            base_time *= 1.4  # Approximate SC delta
        elif self.config.vsc_laps and state.current_lap in self.config.vsc_laps:
            base_time *= 1.3  # Approximate VSC delta
            
        return base_time + noise

class StochasticCompetitorModel(CompetitorModel):
    """
    Wraps the CompetitorModel to add uncertainty to the competitors' base pace.
    """
    def __init__(self, competitors: List[Dict], config: UncertaintyConfig, rng: np.random.Generator):
        # We perturb the initial pace of each competitor slightly
        stochastic_comps = copy.deepcopy(competitors)
        for comp in stochastic_comps:
            pace_noise = rng.normal(0, config.competitor_pace_std)
            comp['recent_pace'] += pace_noise
            
        super().__init__(stochastic_comps)
        self.config = config
        self.rng = rng
        
    def simulate_lap(self):
        # We use the base class behavior which applies standard fuel burn.
        # Could add per-lap noise here if desired, but initial perturbation is sufficient 
        # to create end-of-race variance without extreme cumulative drifting.
        super().simulate_lap()

def run_monte_carlo(
    race_state: RaceState,
    strategy: Strategy,
    base_predictor: MLPredictor,
    base_competitors: List[Dict],
    n_simulations: int = 1000,
    random_seed: int = 42,
    uncertainty_config: UncertaintyConfig = UncertaintyConfig()
) -> List[Dict[str, Any]]:
    """
    Executes a high-performance Monte Carlo simulation for a given strategy.
    Runs the ML trajectory simulator once to establish the exact degradation curve,
    then vector-perturbs lap times and pit stops across N simulations.
    """
    rng = np.random.default_rng(random_seed)
    
    # 1. Run deterministic base trajectory once
    comp_model = CompetitorModel(base_competitors)
    from backend.simulation.pit_loss import get_pit_loss
    base_result = simulate_strategy(
        strategy=strategy,
        initial_state=race_state,
        predictor=base_predictor,
        competitors=comp_model,
        pit_loss_func=get_pit_loss
    )
    
    lap_history = base_result.get("lap_history", [])
    n_laps = len(lap_history)
    n_pits = max(1, base_result.get("pit_stops", len(strategy.pit_laps)))
    base_total_time = base_result.get("total_predicted_time", 0.0)
    base_pos = base_result.get("estimated_finish_position", race_state.current_position)
    
    if n_simulations <= 1:
        base_result['simulation_id'] = 0
        return [base_result]
        
    # 2. Vectorized perturbations for N simulations
    lap_noise_matrix = rng.normal(0, uncertainty_config.lap_time_std, size=(n_simulations, max(1, n_laps)))
    pit_noise_matrix = rng.normal(0, uncertainty_config.pit_loss_std, size=(n_simulations, n_pits))
    
    total_lap_noise = lap_noise_matrix.sum(axis=1)
    total_pit_noise = pit_noise_matrix.sum(axis=1)
    
    mc_results = []
    for sim_id in range(n_simulations):
        sim_total_time = float(base_total_time + total_lap_noise[sim_id] + total_pit_noise[sim_id])
        delta_seconds = sim_total_time - base_total_time
        pos_shift = int(np.round(delta_seconds / 7.0 + rng.normal(0, 0.3)))
        sim_pos = int(np.clip(base_pos + pos_shift, 1, 20))
        
        mc_results.append({
            "strategy_name": strategy.name,
            "pit_laps": strategy.pit_laps,
            "total_predicted_time": sim_total_time,
            "estimated_finish_position": sim_pos,
            "pit_stops": base_result.get("pit_stops", len(strategy.pit_laps)),
            "simulation_id": sim_id
        })
        
    return mc_results
