# Phase 5: Machine Learning Report

## 1. Objective
To construct causal, leakage-safe Machine Learning models for lap-time prediction, tyre degradation, and pit-stop decision making.

## 2. Dataset and Split
- **Total Laps Used**: 67204
- **Train Races**: 50 (Chronologically older)
- **Test Races**: 13 (Chronologically newer)
- **Leakage Prevention**: Random splitting was STRICTLY avoided. Train and test sets were separated by `raceId` chronologically.

## 3. Lap-Time Prediction (Model 1)
- **Methodology**: Target = `lap_time_seconds`. Baseline linear models compared against Tree ensembles.
- **Results**: XGBoost achieved the best validation metrics on the holdout season.
- **Features**: compound, tyre_age, recent_pace, race_progress, laps_remaining, TrackTemp, AirTemp

## 4. Tyre Performance Prediction (Model 2)
- **Methodology**: Target = `lap_time_seconds`. Restricted feature set focusing primarily on `tyre_age` and `compound`. This allows isolated strategy simulation in the Monte Carlo engine.
- **Features**: compound, tyre_age, race_progress, TrackTemp

## 5. Pit-Stop Decision (Model 3)
- **Methodology**: Causal Target Generation: `pit_now = 1` if `Stint` on Lap N+1 > `Stint` on Lap N. Class weights applied due to extreme imbalance (pits are ~2% of laps).
- **Results**: Recall was prioritized over pure accuracy to ensure the Pit-Wall engine detects real pit windows.
- **Features**: compound, tyre_age, recent_pace, laps_remaining, race_progress

## 6. Integration Readiness
Models have been saved to `models/v1/` as `.joblib` pipelines. The FastAPI backend will load these via `joblib.load()` and pass incoming JSON payloads directly to `model.predict(pd.DataFrame(payload))`.

## 7. Limitations
- ML predictions assume standard racing conditions. Unusual traffic, Safety Cars, or erratic driver behavior will cause real-world divergence from predictions.
- Gap-ahead/behind features were excluded due to extraction complexity from the raw flat file, meaning traffic effects are generalized rather than explicit.
