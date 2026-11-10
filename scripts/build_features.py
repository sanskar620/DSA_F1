import os
import pandas as pd
import numpy as np

def build_features():
    print("Loading cleaned data...")
    laps_df = pd.read_parquet(os.path.join("data", "processed", "clean_lap_data.parquet"))
    race_df = pd.read_parquet(os.path.join("data", "processed", "clean_race_data.parquet"))
    
    print("Building features...")
    
    # Sort strictly chronologically
    # In our flat dataset, driverId might be 'Driver' (number) for FastF1, or 'driverId' for f1_all
    if 'driverId' not in laps_df.columns and 'Driver' in laps_df.columns:
        laps_df['driverId'] = laps_df['Driver']
        
    laps_df = laps_df.sort_values(by=['raceId', 'driverId', 'LapNumber']).reset_index(drop=True)
    
    # 1. Total Laps (for laps_remaining and race_progress)
    # We find the max laps completed in the race from the race_df results
    max_laps_per_race = race_df.groupby('race_id')['laps_completed'].max().reset_index()
    max_laps_per_race.columns = ['raceId', 'total_race_laps']
    
    features_df = pd.merge(laps_df, max_laps_per_race, on='raceId', how='left')
    
    # Some races might not map perfectly if FastF1 used a placeholder raceId, fallback to max LapNumber
    fallback_max_laps = laps_df.groupby('raceId')['LapNumber'].max().reset_index()
    fallback_max_laps.columns = ['raceId', 'fallback_total']
    features_df = pd.merge(features_df, fallback_max_laps, on='raceId', how='left')
    features_df['total_race_laps'] = features_df['total_race_laps'].fillna(features_df['fallback_total'])
    
    # 2. Race Context Features
    features_df['laps_remaining'] = features_df['total_race_laps'] - features_df['LapNumber']
    # Prevent negative laps remaining if someone exceeded expected max
    features_df.loc[features_df['laps_remaining'] < 0, 'laps_remaining'] = 0 
    
    features_df['race_progress'] = features_df['LapNumber'] / features_df['total_race_laps']
    
    # 3. Tyre Features
    # Use TyreLife as tyre_age directly
    features_df['tyre_age'] = features_df['TyreLife']
    features_df['compound'] = features_df['Compound']
    
    # 4. Pace Features & Leakage Prevention (CRITICAL)
    # Group by race and driver to calculate pace
    grouped = features_df.groupby(['raceId', 'driverId'])
    
    # recent_pace: rolling mean of last 3 laps, SHIFTED BY 1 so we don't peek at the current lap time!
    # Because we want to predict lap N, we can only know pace of N-1, N-2, N-3.
    features_df['recent_pace'] = grouped['lap_time_seconds'].transform(
        lambda x: x.shift(1).rolling(window=3, min_periods=1).mean()
    )
    
    # pace_trend: difference between last lap and the 3-lap rolling average before it
    features_df['pace_trend'] = features_df.groupby(['raceId', 'driverId'])['lap_time_seconds'].shift(1) - features_df['recent_pace']
    
    # 5. Position
    features_df['position'] = features_df['position_x']
    
    # 6. Select final ML ready columns
    ml_cols = [
        'raceId', 'driverId', 'LapNumber', 'position', 'lap_time_seconds',
        'compound', 'tyre_age', 'Stint', 'recent_pace', 'pace_trend',
        'laps_remaining', 'race_progress', 'total_race_laps',
        'AirTemp', 'TrackTemp', 'Rainfall'
    ]
    
    # Ensure all exist
    avail_cols = [c for c in ml_cols if c in features_df.columns]
    
    final_features = features_df[avail_cols].copy()
    
    out_path = os.path.join("data", "processed", "ml_features.parquet")
    final_features.to_parquet(out_path, index=False)
    print(f"Saved {len(final_features)} feature rows to {out_path}")
    
    # Generate Feature Dictionary
    dict_content = """# Feature Dictionary

| Feature | Description | Type | Unit | Source | Leakage Safe? |
|---------|-------------|------|------|--------|---------------|
| raceId | Unique Race ID | Identifier | - | Database | YES |
| driverId | Unique Driver ID | Identifier | - | Database | YES |
| LapNumber | Current Lap Number | Numeric | laps | Telemetry | YES |
| position | Driver's track position | Numeric | rank | Telemetry | YES |
| lap_time_seconds | Target Variable: Time taken to complete the lap | Numeric | seconds | Telemetry | N/A (TARGET) |
| compound | Standardized Tyre Compound (SOFT, MEDIUM, HARD, etc.) | Categorical | - | Telemetry | YES |
| tyre_age | Laps completed on current tyre | Numeric | laps | Telemetry | YES |
| Stint | Current tyre stint number | Numeric | count | Telemetry | YES |
| recent_pace | Rolling mean of the PREVIOUS 3 laps | Numeric | seconds | Derived | YES (Shifted by 1) |
| pace_trend | Difference between last lap and recent_pace | Numeric | seconds | Derived | YES (Shifted by 1) |
| laps_remaining | Laps left in the race | Numeric | laps | Derived | YES |
| race_progress | Fraction of race completed (0.0 to 1.0) | Numeric | ratio | Derived | YES |
| AirTemp | Ambient Air Temperature | Numeric | °C | Weather | YES |
| TrackTemp | Track Surface Temperature | Numeric | °C | Weather | YES |
| Rainfall | Rainfall indicator / intensity | Numeric | bool/mm | Weather | YES |

> [!IMPORTANT]
> **Leakage Prevention applied:** `recent_pace` and `pace_trend` are strictly calculated using `.shift(1)`. When predicting the lap time for Lap `N`, the model only has access to the pace history up to Lap `N-1`.
"""
    with open(os.path.join("docs", "feature_dictionary.md"), "w", encoding="utf-8") as f:
        f.write(dict_content)
        
    print("Feature building complete.")

if __name__ == "__main__":
    build_features()
