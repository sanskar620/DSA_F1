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
    Executes a Monte Carlo simulation for a given strategy.
    Re-uses Phase 6's simulate_strategy without duplicating core logic.
    """
    # Use a seed for perfect reproducibility
    rng = np.random.default_rng(random_seed)
    
    mc_results = []
    
    for sim_id in range(n_simulations):
        # 1. Create Stochastic wrappers
        stoch_predictor = StochasticPredictor(base_predictor, uncertainty_config, rng)
        stoch_competitors = StochasticCompetitorModel(base_competitors, uncertainty_config, rng)
        
        # We need to inject pit loss uncertainty. The original simulator calls get_pit_loss directly.
        # Since we cannot easily monkey-patch get_pit_loss natively without side effects, 
        # a better way is to override it temporarily, or just let Phase 6 accept a pit_loss_func.
        # Wait, the prompt says "Do not copy Phase 6 simulation logic".
        # We will modify Phase 6 slightly to accept an optional pit_loss_func kwargs if not already done.
        
        from backend.simulation.pit_loss import get_pit_loss
        # 2. Run deterministic simulator
        result = simulate_strategy(
            strategy=strategy,
            initial_state=race_state,
            predictor=stoch_predictor,
            competitors=stoch_competitors,
            pit_loss_func=lambda c: get_pit_loss(c) + rng.normal(0, uncertainty_config.pit_loss_std)
        )
        
        result['simulation_id'] = sim_id
        mc_results.append(result)
        
    return mc_results
