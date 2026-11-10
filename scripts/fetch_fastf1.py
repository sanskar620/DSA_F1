import os
import fastf1
import pandas as pd

# Suppress SettingWithCopyWarning from pandas that fastf1 sometimes triggers
pd.options.mode.chained_assignment = None

CACHE_DIR = os.path.join("data", "raw", "fastf1_cache")
OUTPUT_DIR = os.path.join("data", "raw", "fastf1")

def ensure_dir(path):
    if not os.path.exists(path):
        os.makedirs(path)

def fetch_race_data(year, round_num, race_name, year_dir):
    """Fetches and saves all relevant FastF1 data for a single race."""
    race_dir = os.path.join(year_dir, f"Round_{round_num}_{race_name}")
    ensure_dir(race_dir)
    
    lap_cache = os.path.join(race_dir, "laps.csv")
    
    # We check if laps.csv exists to avoid re-running if already downloaded
    if os.path.exists(lap_cache):
        print(f"Skipping {year} Round {round_num}, already cached in {race_dir}.")
        return

    print(f"Loading {year} Round {round_num}: {race_name}...")
    
    try:
        # Load the race session. We need telemetry=True to get accurate sector times and compound data
        session = fastf1.get_session(year, round_num, 'R')
        session.load(telemetry=True, weather=True, messages=True)
        
        # 1. Laps, Drivers, Tyre Stints, Sector Times
        if session.laps is not None and not session.laps.empty:
            session.laps.to_csv(lap_cache, index=False)
            print(f"  - Saved laps data (includes tyres, sectors, positions)")
            
        # 2. Weather (Track Temp, Air Temp, Rainfall, etc.)
        if session.weather_data is not None and not session.weather_data.empty:
            weather_cache = os.path.join(race_dir, "weather.csv")
            session.weather_data.to_csv(weather_cache, index=False)
            print(f"  - Saved weather data")
            
        # 3. Track Status (Green, Yellow, SC, VSC)
        if session.track_status is not None and not session.track_status.empty:
            status_cache = os.path.join(race_dir, "track_status.csv")
            session.track_status.to_csv(status_cache, index=False)
            print(f"  - Saved track status")
            
        # 4. Race Control Messages
        if session.race_control_messages is not None and not session.race_control_messages.empty:
            messages_cache = os.path.join(race_dir, "race_control_messages.csv")
            session.race_control_messages.to_csv(messages_cache, index=False)
            print(f"  - Saved race control messages")

        print(f"Successfully finished {year} Round {round_num}.\n")
        
    except Exception as e:
        print(f"Failed to load {year} Round {round_num}: {e}\n")


def main():
    ensure_dir(CACHE_DIR)
    ensure_dir(OUTPUT_DIR)
    
    # Enable FastF1 caching to avoid re-downloading source data from API
    fastf1.Cache.enable_cache(CACHE_DIR)
    
    seasons = [2021, 2022, 2023, 2024]
    
    for year in seasons:
        year_dir = os.path.join(OUTPUT_DIR, str(year))
        ensure_dir(year_dir)
        
        print(f"Fetching schedule for {year}...")
        try:
            schedule = fastf1.get_event_schedule(year)
        except Exception as e:
            print(f"Failed to get schedule for {year}: {e}")
            continue
            
        # For demonstration and limiting API bombardment during development,
        # we will fetch just the first 2 races of each season.
        # To fetch all, replace `races_to_fetch` with: schedule['RoundNumber'].dropna().tolist()
        races_to_fetch = [1, 2] 
        
        for round_num in races_to_fetch:
            if pd.isna(round_num) or round_num == 0:
                continue
                
            round_num = int(round_num)
            
            # Find the event in the schedule
            event = schedule[schedule['RoundNumber'] == round_num].iloc[0]
            race_name = str(event['EventName']).replace(' ', '_').replace('/', '_')
            
            fetch_race_data(year, round_num, race_name, year_dir)

if __name__ == "__main__":
    main()
