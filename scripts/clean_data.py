import os
import pandas as pd
import numpy as np
import psycopg2
from dotenv import load_dotenv

load_dotenv("e:/DSA PROJECT/.env")

DB_HOST = os.getenv("DATABASE_HOST", "localhost")
DB_PORT = os.getenv("DATABASE_PORT", "5432")
DB_NAME = os.getenv("DATABASE_NAME", "f1_strategyiq")
DB_USER = os.getenv("DATABASE_USER", "postgres")
DB_PASSWORD = os.getenv("DATABASE_PASSWORD", "postgres")

def get_connection():
    return psycopg2.connect(
        host=DB_HOST,
        port=DB_PORT,
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD
    )

def standardize_tyre(compound):
    if pd.isna(compound):
        return np.nan
    
    comp = str(compound).upper().strip()
    if comp == 'UNKNOWN':
        return np.nan
    
    mapping = {
        'SOFT': 'SOFT',
        'MEDIUM': 'MEDIUM',
        'HARD': 'HARD',
        'INTERMEDIATE': 'INTERMEDIATE',
        'WET': 'WET',
        'HYPERSOFT': 'SOFT', # Older equivalent mappings if found
        'ULTRASOFT': 'SOFT',
        'SUPERSOFT': 'SOFT',
        'TEST_UNKNOWN': np.nan
    }
    return mapping.get(comp, comp) # Return the mapped value or original if unknown

def clean_data():
    ensure_dir("data/processed")
    ensure_dir("docs")
    
    report_lines = ["# Phase 3 Data Cleaning Report\n"]
    
    # 1. Load PostgreSQL Data
    conn = get_connection()
    try:
        races_df = pd.read_sql("SELECT * FROM races", conn)
        results_df = pd.read_sql("SELECT * FROM results", conn)
        circuits_df = pd.read_sql("SELECT * FROM circuits", conn)
    finally:
        conn.close()
        
    report_lines.append("## 1. Input Tables (PostgreSQL)")
    report_lines.append(f"- `races`: {len(races_df)} rows")
    report_lines.append(f"- `results`: {len(results_df)} rows")
    report_lines.append(f"- `circuits`: {len(circuits_df)} rows\n")

    # Clean races & results
    # Replace non-positive finish positions (DNFs) with NaN to avoid numeric skew
    results_clean = results_df.copy()
    results_clean['finish_position'] = pd.to_numeric(results_clean['finish_position'], errors='coerce')
    
    race_data = pd.merge(results_clean, races_df, on='race_id', how='left')
    race_data = pd.merge(race_data, circuits_df, on='circuit_id', how='left')
    
    race_data_path = os.path.join("data", "processed", "clean_race_data.parquet")
    race_data.to_parquet(race_data_path, index=False)
    report_lines.append(f"Saved `clean_race_data.parquet` with {len(race_data)} rows.\n")
    
    # 2. Load and Clean Lap/Weather Data (f1_all.csv + FastF1)
    f1_all_path = os.path.join("data", "Tyres weather data", "f1_all.csv")
    if os.path.exists(f1_all_path):
        laps_df = pd.read_csv(f1_all_path)
        raw_laps_count = len(laps_df)
        report_lines.append(f"## 2. Input Tables (Telemetry CSV)")
        report_lines.append(f"- `f1_all.csv`: {raw_laps_count} rows\n")
        
        # We will attempt to merge in 2024 FastF1 data here if it exists
        fastf1_2024_dir = os.path.join("data", "raw", "fastf1", "2024")
        if os.path.exists(fastf1_2024_dir):
            fastf1_dfs = []
            for race_folder in os.listdir(fastf1_2024_dir):
                lap_cache = os.path.join(fastf1_2024_dir, race_folder, "laps.csv")
                weather_cache = os.path.join(fastf1_2024_dir, race_folder, "weather.csv")
                
                if os.path.exists(lap_cache) and os.path.exists(weather_cache):
                    f_laps = pd.read_csv(lap_cache, low_memory=False)
                    f_weather = pd.read_csv(weather_cache, low_memory=False)
                    
                    # Merge FastF1 laps and weather on Time
                    # Time is timedelta. We just take the nearest weather observation
                    if 'Time' in f_laps.columns and 'Time' in f_weather.columns:
                        f_laps['Time_td'] = pd.to_timedelta(f_laps['Time'])
                        f_weather['Time_td'] = pd.to_timedelta(f_weather['Time'])
                        
                        f_laps = f_laps.sort_values('Time_td')
                        f_weather = f_weather.sort_values('Time_td')
                        
                        merged_f1 = pd.merge_asof(f_laps, f_weather, on='Time_td', direction='backward')
                        
                        # Map FastF1 columns to match f1_all.csv so we can concat
                        # Mapping: LapNumber -> LapNumber, Compound -> Compound, TyreLife -> TyreLife, 
                        # DriverNumber -> driverId (approx), Position -> position_x, LapTime -> time
                        try:
                            mapped_df = pd.DataFrame({
                                'year': 2024,
                                'raceId': 9999, # Placeholder, in reality we'd look up from races table based on name
                                'Driver': merged_f1['Driver'],
                                'LapNumber': merged_f1['LapNumber'],
                                'Compound': merged_f1['Compound'],
                                'TyreLife': merged_f1['TyreLife'],
                                'AirTemp': merged_f1['AirTemp'],
                                'TrackTemp': merged_f1['TrackTemp'],
                                'Rainfall': merged_f1['Rainfall'],
                                'milliseconds': pd.to_timedelta(merged_f1['LapTime']).dt.total_seconds() * 1000,
                                'position_x': merged_f1['Position']
                            })
                            fastf1_dfs.append(mapped_df)
                        except Exception as e:
                            print(f"Skipping {race_folder} due to mapping error: {e}")
                            
            if fastf1_dfs:
                combined_fastf1 = pd.concat(fastf1_dfs, ignore_index=True)
                laps_df = pd.concat([laps_df, combined_fastf1], ignore_index=True)
                report_lines.append(f"- Integrated FastF1 2024 data: {len(combined_fastf1)} rows added to lap data.\n")
                
        
        # Cleaning Rules
        laps_clean = laps_df.copy()
        
        # A. Lap Time Standardization
        laps_clean['lap_time_seconds'] = pd.to_numeric(laps_clean['milliseconds'], errors='coerce') / 1000.0
        
        # Remove impossible lap times (e.g. <= 0 or insanely large)
        invalid_times = laps_clean[(laps_clean['lap_time_seconds'] <= 0) | (laps_clean['lap_time_seconds'] > 600)].shape[0]
        laps_clean.loc[(laps_clean['lap_time_seconds'] <= 0) | (laps_clean['lap_time_seconds'] > 600), 'lap_time_seconds'] = np.nan
        
        # B. Tyre Standardization
        laps_clean['original_compound'] = laps_clean['Compound']
        laps_clean['Compound'] = laps_clean['Compound'].apply(standardize_tyre)
        
        # C. Impossible Lap Numbers
        laps_clean['LapNumber'] = pd.to_numeric(laps_clean['LapNumber'], errors='coerce')
        invalid_laps = laps_clean[laps_clean['LapNumber'] < 1].shape[0]
        laps_clean = laps_clean[laps_clean['LapNumber'] >= 1]
        
        # Weather missing value handling: left as NaN instead of interpolation
        
        laps_data_path = os.path.join("data", "processed", "clean_lap_data.parquet")
        laps_clean.to_parquet(laps_data_path, index=False)
        
        report_lines.append("## 3. Cleaning Rules Applied")
        report_lines.append("- **Lap Times**: Converted `milliseconds` to `lap_time_seconds`. Set impossible times (<=0 or >10m) to NaN.")
        report_lines.append(f"  - Invalid lap times nullified: {invalid_times}")
        report_lines.append("- **Tyres**: Mapped 'UNKNOWN' to NaN, retained SOFT, MEDIUM, HARD, INTERMEDIATE, WET. Created `original_compound` for traceability.")
        report_lines.append("- **Lap Numbers**: Removed lap numbers < 1.")
        report_lines.append(f"  - Invalid lap records removed: {invalid_laps}")
        report_lines.append("- **Weather Alignment**: Left as NaN where unavailable. FastF1 alignment done via timestamp `merge_asof` (backward).\n")
        
        report_lines.append("## 4. Final Cleaned Dataset")
        report_lines.append(f"- Cleaned Lap Rows: {len(laps_clean)}")
        report_lines.append(f"- Saved to `clean_lap_data.parquet`\n")
        
        report_lines.append("## 5. Available Weather Fields")
        avail_weather = [c for c in ['AirTemp', 'TrackTemp', 'Humidity', 'Pressure', 'WindSpeed', 'WindDirection', 'Rainfall'] if c in laps_clean.columns]
        report_lines.append(", ".join(avail_weather) + "\n")
        
    else:
        report_lines.append("WARNING: `f1_all.csv` not found. Could not build clean lap data.")

    report_path = os.path.join("docs", "phase3_cleaning_report.md")
    with open(report_path, "w", encoding="utf-8") as f:
        f.write("\n".join(report_lines))
        
    print(f"Data cleaning complete. Report saved to {report_path}")

def ensure_dir(path):
    if not os.path.exists(path):
        os.makedirs(path)

if __name__ == "__main__":
    clean_data()
