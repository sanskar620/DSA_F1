from fastapi import APIRouter, Depends, HTTPException
import pandas as pd
from backend.api.schemas.pitwall import PitWallDecisionRequest, ReplayRequest
from backend.api.dependencies import get_predictor
from backend.simulation.ml_integration import MLPredictor
from backend.api.routes.strategy import _convert_state
from backend.pitwall.decision_engine import evaluate_pit_decision
from backend.pitwall.replay_engine import run_race_replay

router = APIRouter()

@router.post("/decision")
def pitwall_decision(request: PitWallDecisionRequest, predictor: MLPredictor = Depends(get_predictor)):
    try:
        state = _convert_state(request.race_state)
        # Dummy competitors list for now
        decision = evaluate_pit_decision(state, [], predictor, request.objective, request.simulation_count)
        return {"success": True, "data": decision}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/replay")
def pitwall_replay(request: ReplayRequest, predictor: MLPredictor = Depends(get_predictor)):
    try:
        # This requires reading historical features from DB or parquet
        try:
            df_hist = pd.read_parquet("data/processed/ml_features.parquet")
        except:
            raise HTTPException(status_code=503, detail="Historical features not found")
            
        res = run_race_replay(
            df_hist, 
            request.race_id, 
            request.driver_id, 
            request.start_lap, 
            request.objective, 
            request.simulation_count, 
            predictor
        )
        return {"success": True, "data": res}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
