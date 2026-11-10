from fastapi import APIRouter, Depends, HTTPException
from backend.api.schemas.prediction import LapTimeRequest, LapTimeResponse, PitDecisionResponse
from backend.api.dependencies import get_predictor
from backend.simulation.ml_integration import MLPredictor
from backend.simulation.state import RaceState

router = APIRouter()

def _build_race_state(request: LapTimeRequest) -> RaceState:
    total_laps = request.total_laps or 57
    laps_remaining = request.laps_remaining if request.laps_remaining is not None else max(1, total_laps - request.lap_number)
    recent_pace = request.recent_pace if request.recent_pace is not None else 90.5
    circuit = request.circuit or "Monza"
    driver = request.driver or str(request.driver_id)
    constructor = request.constructor or "Formula 1 Team"
    track_temp = request.track_temp if request.track_temp is not None else 30.0
    air_temp = request.air_temp if request.air_temp is not None else 25.0
    gap_ahead = request.gap_ahead if request.gap_ahead is not None else 1.5
    gap_behind = request.gap_behind if request.gap_behind is not None else 2.0
    pit_stops_taken = request.pit_stops_taken if request.pit_stops_taken is not None else 1

    return RaceState(
        race_id=request.race_id,
        circuit=circuit,
        driver=driver,
        constructor=constructor,
        current_lap=request.lap_number,
        total_laps=total_laps,
        laps_remaining=laps_remaining,
        current_position=request.current_position,
        compound=request.compound,
        tyre_age=request.tyre_age,
        stint=pit_stops_taken + 1,
        stint_lap=request.tyre_age,
        recent_pace=recent_pace,
        gap_ahead=gap_ahead,
        gap_behind=gap_behind,
        cumulative_time=round(request.lap_number * recent_pace),
        pit_stops_taken=pit_stops_taken,
        track_temp=track_temp,
        air_temp=air_temp,
        rainfall=0.0,
        track_status="1"
    )

@router.post("/predict/lap-time", response_model=LapTimeResponse)
def predict_lap_time(request: LapTimeRequest, predictor: MLPredictor = Depends(get_predictor)):
    try:
        state = _build_race_state(request)
        predicted_time = predictor.predict_lap_time(state)
        
        return LapTimeResponse(
            predicted_lap_time=predicted_time,
            model="lap_time_model",
            model_version="v1"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/predict/tyre")
def predict_tyre(request: LapTimeRequest, predictor: MLPredictor = Depends(get_predictor)):
    try:
        state = _build_race_state(request)
        deg_factor = predictor.predict_tyre_degradation(state)
        return {
            "predicted_degradation_factor": deg_factor,
            "note": "Phase 5 tyre model is a hybrid analytical/ML component."
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/predict/pit-decision", response_model=PitDecisionResponse)
def predict_pit_decision(request: LapTimeRequest, predictor: MLPredictor = Depends(get_predictor)):
    try:
        state = _build_race_state(request)
        pit_prob = predictor.predict_pit_decision(state)
        return PitDecisionResponse(
            decision="PIT NOW" if pit_prob >= 0.5 else "STAY OUT",
            pit_probability=pit_prob,
            stay_out_probability=1.0 - pit_prob
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
