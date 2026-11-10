import os
import pandas as pd
import glob

def inspect_csv(file_path, is_weather_tyre=False):
    print(f"\n{'='*50}")
    print(f"Inspecting File: {os.path.basename(file_path)}")
    print(f"{'='*50}")
    
    try:
        # low_memory=False to avoid mixed type warnings on large files
        df = pd.read_csv(file_path, low_memory=False)
    except Exception as e:
        print(f"Error reading file: {e}")
        return

    # Basic stats
    print(f"Rows: {df.shape[0]}")
    print(f"Columns: {df.shape[1]}")
    print(f"Column Names: {list(df.columns)}")
    print(f"Duplicate Rows: {df.duplicated().sum()}")
    print("\nData Types:")
    print(df.dtypes.to_string())
    
    print("\nMissing Values (Count / Percentage):")
    missing = df.isnull().sum()
    missing_pct = (missing / df.shape[0]) * 100
    for col in df.columns:
        if missing[col] > 0:
            print(f"  {col}: {missing[col]} ({missing_pct[col]:.2f}%)")
            
    print("\nUnique Values per column:")
    for col in df.columns:
        print(f"  {col}: {df[col].nunique()}")
        
    def find_col(*keywords):
        for c in df.columns:
            cl = c.lower()
            if any(k in cl for k in keywords):
                return c
        return None
        
    season_col = find_col('year', 'season')
    race_col = find_col('raceid', 'round', 'race')
    driver_col = find_col('driverid', 'driver')
    constructor_col = find_col('constructorid', 'constructor', 'team')
    circuit_col = find_col('circuitid', 'circuit')
    
    print("\nAggregated F1 Stats (Detected):")
    if season_col:
        print(f"  Season/Year Range: {df[season_col].min()} - {df[season_col].max()}")
    if race_col:
        print(f"  Number of Races: {df[race_col].nunique()}")
    if driver_col:
        print(f"  Number of Drivers: {df[driver_col].nunique()}")
    if constructor_col:
        print(f"  Number of Constructors: {df[constructor_col].nunique()}")
    if circuit_col:
        print(f"  Number of Circuits: {df[circuit_col].nunique()}")
        
    if is_weather_tyre:
        print("\n--- Weather & Tyre Specific Analysis ---")
        
        # Detect columns intelligently
        tyre_cols = [c for c in df.columns if 'tyre' in c.lower() or 'compound' in c.lower()]
        tyre_age_cols = [c for c in df.columns if 'age' in c.lower() and 'tyre' in c.lower()]
        lap_cols = [c for c in df.columns if 'lap' in c.lower()]
        lap_time_cols = [c for c in df.columns if 'time' in c.lower() and 'lap' in c.lower()]
        weather_cols = [c for c in df.columns if 'weather' in c.lower()]
        track_temp_cols = [c for c in df.columns if 'track' in c.lower() and 'temp' in c.lower()]
        air_temp_cols = [c for c in df.columns if 'air' in c.lower() and 'temp' in c.lower()]
        rain_cols = [c for c in df.columns if 'rain' in c.lower() or 'precip' in c.lower()]
        wind_cols = [c for c in df.columns if 'wind' in c.lower()]
        track_status_cols = [c for c in df.columns if 'status' in c.lower() and 'track' in c.lower()]
        pit_stop_cols = [c for c in df.columns if 'pit' in c.lower()]
        
        print(f"Tyre-related columns: {tyre_cols}")
        print(f"Tyre age columns: {tyre_age_cols}")
        print(f"Lap-related columns: {lap_cols}")
        print(f"Lap-time columns: {lap_time_cols}")
        print(f"Weather columns: {weather_cols}")
        print(f"Track-temperature columns: {track_temp_cols}")
        print(f"Air-temperature columns: {air_temp_cols}")
        print(f"Rainfall/precipitation columns: {rain_cols}")
        print(f"Wind-related columns: {wind_cols}")
        print(f"Track-status columns: {track_status_cols}")
        print(f"Pit-stop-related columns: {pit_stop_cols}")
        
        compound_col = find_col('compound')
        if compound_col:
            print(f"Compound values: {df[compound_col].unique()}")

    print("\nSample Rows:")
    print(df.head(3))

if __name__ == "__main__":
    historical_dir = os.path.join("data", "Historical data")
    weather_tyre_dir = os.path.join("data", "Tyres weather data")
    
    if os.path.exists(historical_dir):
        historical_files = glob.glob(os.path.join(historical_dir, "*.csv"))
        for f in historical_files:
            inspect_csv(f, is_weather_tyre=False)
    else:
        print(f"Warning: {historical_dir} not found.")
            
    if os.path.exists(weather_tyre_dir):
        weather_files = glob.glob(os.path.join(weather_tyre_dir, "*.csv"))
        for f in weather_files:
            inspect_csv(f, is_weather_tyre=True)
    else:
        print(f"Warning: {weather_tyre_dir} not found.")
