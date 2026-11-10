from fastapi import APIRouter, Depends, HTTPException
from typing import Any
import pandas as pd
from backend.api.schemas.strategy import SimulateRequest, MonteCarloRequest, OptimizeRequest
from backend.api.dependencies import get_predictor
from backend.simulation.ml_integration import MLPredictor
from backend.simulation.state import RaceState, Strategy
from backend.simulation.race_simulator import simulate_strategy
from backend.simulation.monte_carlo import run_monte_carlo, UncertaintyConfig
from backend.simulation.results import aggregate_monte_carlo_results
from backend.optimization.optimizer import optimize_strategies

router = APIRouter()

def _convert_state(req_state) -> RaceState:
    return RaceState(
        race_id=req_state.race_id,
        circuit=req_state.circuit,
        driver=req_state.driver,
        constructor=req_state.constructor,
        current_lap=req_state.current_lap,
        total_laps=req_state.total_laps,
        laps_remaining=req_state.laps_remaining,
        current_position=req_state.current_position,
        compound=req_state.compound,
        tyre_age=req_state.tyre_age,
        stint=req_state.stint,
        stint_lap=req_state.stint_lap,
        recent_pace=req_state.recent_pace,
        gap_ahead=req_state.gap_ahead,
        gap_behind=req_state.gap_behind,
        cumulative_time=req_state.cumulative_time,
        pit_stops_taken=req_state.pit_stops_taken,
        track_temp=req_state.track_temp,
        air_temp=req_state.air_temp,
        rainfall=req_state.rainfall,
        track_status=req_state.track_status
    )

def _convert_strategy(req_strat) -> Strategy:
    return Strategy(
        name=req_strat.name,
        starting_compound=req_strat.starting_compound,
        planned_compounds=req_strat.planned_compounds,
        pit_laps=req_strat.pit_laps
    )

@router.post("/simulate")
def simulate(request: SimulateRequest, predictor: MLPredictor = Depends(get_predictor)):
    try:
        state = _convert_state(request.race_state)
        strategy = _convert_strategy(request.strategy)
        
        # dummy competitor list
        from backend.simulation.competitor_model import CompetitorModel
        dummy_comps = CompetitorModel([])
        
        result = simulate_strategy(strategy, state, predictor, dummy_comps)
        return {"success": True, "data": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/monte-carlo")
def monte_carlo(request: MonteCarloRequest, predictor: MLPredictor = Depends(get_predictor)):
    try:
        state = _convert_state(request.race_state)
        strategy = _convert_strategy(request.strategy)
        
        config = UncertaintyConfig(lap_time_std=1.5, pit_loss_std=1.0, competitor_pace_std=0.5)
        
        # dummy base competitors for now
        mc_results = run_monte_carlo(
            state, strategy, predictor, [], 
            request.simulation_count, request.random_seed, config
        )
        
        summary = aggregate_monte_carlo_results(mc_results)
        
        # Extract row corresponding to this strategy
        strat_summary = summary[summary['Strategy'] == strategy.name].iloc[0].to_dict()
        
        return {"success": True, "data": strat_summary}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/optimize")
def optimize(request: OptimizeRequest, predictor: MLPredictor = Depends(get_predictor)):
    try:
        import numpy as np
        state = _convert_state(request.race_state)
        candidate_strategies = [_convert_strategy(s) for s in request.candidate_strategies]
        
        unc_config = UncertaintyConfig(lap_time_std=1.5, pit_loss_std=1.0, competitor_pace_std=0.5)
        driver_val = getattr(request.race_state, 'driver_id', None) or 1
        seed = int((request.race_state.race_id * 31 + driver_val * 17 + abs(hash(request.objective))) % 10000 + 1)
        
        all_results = []
        for idx, strat in enumerate(candidate_strategies):
            mc = run_monte_carlo(state, strat, predictor, [], request.simulation_count, seed + idx * 7, unc_config)
            all_results.extend(mc)
            
        # Dynamically compute finish positions based on driver position and relative time deltas
        all_times = [r['total_predicted_time'] for r in all_results]
        median_time = float(np.median(all_times))
        driver_grid_pos = max(1, min(20, request.race_state.current_position))
        rng = np.random.default_rng(seed)
        
        for r in all_results:
            delta = r['total_predicted_time'] - median_time
            pos_noise = rng.normal(0, 0.4)
            r['estimated_finish_position'] = int(np.clip(np.round(driver_grid_pos + (delta / 8.5) + pos_noise), 1, 20))
            
        summary_df = aggregate_monte_carlo_results(all_results)
        recommendation = optimize_strategies(summary_df, request.objective)
        
        # Empirical finish position distribution for the winning strategy
        winner_name = recommendation.get("recommended_strategy")
        winner_positions = [r['estimated_finish_position'] for r in all_results if r['strategy_name'] == winner_name]
        pos_dist = []
        for p in range(1, 10):
            prob = float((np.array(winner_positions) == p).mean() * 100.0) if winner_positions else 0.0
            pos_dist.append({"pos": f"P{p}", "prob": round(prob, 1)})
        recommendation["position_distribution"] = pos_dist
        
        return {"success": True, "data": recommendation}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
