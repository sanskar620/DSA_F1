import joblib
import pandas as pd
from backend.simulation.state import RaceState

class MLPredictor:
    def __init__(self, model_dir: str = "models/v1"):
        """Loads Phase 5 artifacts."""
        self.model_dir = model_dir
        self.lap_time_model = joblib.load(f"{model_dir}/lap_time_model.joblib")
        self.lap_time_features = joblib.load(f"{model_dir}/lap_time_features.joblib")
        
        # We also load tyre and pit models but they are exposed separately
        self.tyre_model = joblib.load(f"{model_dir}/tyre_model.joblib")
        self.tyre_features = joblib.load(f"{model_dir}/tyre_features.joblib")
        self.pit_model = joblib.load(f"{model_dir}/pit_decision_model.joblib")
        self.pit_features = joblib.load(f"{model_dir}/pit_decision_features.joblib")

    def predict_lap_time(self, state: RaceState) -> float:
        """
        Predicts the lap time for the given RaceState using Model 1.
        Strictly maps the RaceState to the trained feature list.
        """
        if state.compound not in ["SOFT", "MEDIUM", "HARD", "INTERMEDIATE", "WET"]:
            raise ValueError(f"Invalid compound: {state.compound}")
            
        # Calculate derived features used in training
        race_progress = state.current_lap / state.total_laps if state.total_laps > 0 else 0.0
        
        feature_dict = {
            'compound': state.compound,
            'tyre_age': state.tyre_age,
            'recent_pace': state.recent_pace,
            'race_progress': race_progress,
            'laps_remaining': state.laps_remaining,
            'TrackTemp': state.track_temp,
            'AirTemp': state.air_temp
        }
        
        # Build the exact dataframe the model expects
        df_features = pd.DataFrame([feature_dict])[self.lap_time_features]
        
        # Inference
        predicted_time = self.lap_time_model.predict(df_features)[0]
        return float(predicted_time)

    def predict_pit_decision(self, state: RaceState) -> float:
        """
        Returns the probability (0 to 1) of 'PIT NOW' based on the Phase 5 classifier.
        """
        race_progress = state.current_lap / state.total_laps if state.total_laps > 0 else 0.0
        
        feature_dict = {
            'compound': state.compound,
            'tyre_age': state.tyre_age,
            'recent_pace': state.recent_pace,
            'race_progress': race_progress,
            'laps_remaining': state.laps_remaining
        }
        
        # Inference with preloaded model
        df_features = pd.DataFrame([feature_dict])[self.pit_features]
        
        # Binary classifier (0 = STAY OUT, 1 = PIT NOW)
        proba = self.pit_model.predict_proba(df_features)[0]
        return float(proba[1]) # probability of class 1 (PIT NOW)

    def predict_tyre_degradation(self, state: RaceState) -> float:
        """
        Returns the predicted tyre degradation factor using Phase 5 tyre model.
        """
        race_progress = state.current_lap / state.total_laps if state.total_laps > 0 else 0.0
        
        feature_dict = {
            'compound': state.compound,
            'tyre_age': state.tyre_age,
            'race_progress': race_progress,
            'TrackTemp': state.track_temp
        }
        
        df_features = pd.DataFrame([feature_dict])[self.tyre_features]
        deg_factor = self.tyre_model.predict(df_features)[0]
        return float(deg_factor)
