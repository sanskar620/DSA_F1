import os
import pandas as pd
import numpy as np
import psycopg2
from psycopg2 import extras
from psycopg2.extensions import register_adapter, AsIs
from dotenv import load_dotenv

register_adapter(np.int64, AsIs)
register_adapter(np.float64, AsIs)

# Load environment variables
load_dotenv()

DB_HOST = os.getenv("DATABASE_HOST", "localhost")
DB_PORT = os.getenv("DATABASE_PORT", "5432")
DB_NAME = os.getenv("DATABASE_NAME", "f1_strategyiq")
DB_USER = os.getenv("DATABASE_USER", "postgres")
DB_PASSWORD = os.getenv("DATABASE_PASSWORD", "")

HISTORICAL_DIR = os.path.join("data", "Historical data")
WEATHER_TYRE_DIR = os.path.join("data", "Tyres weather data")

def get_connection():
    return psycopg2.connect(
        host=DB_HOST,
        port=DB_PORT,
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD
    )

def execute_schema(conn):
    schema_path = os.path.join("database", "schema", "schema.sql")
    if not os.path.exists(schema_path):
        print(f"Schema file not found at {schema_path}")
        return
        
    with open(schema_path, "r", encoding="utf-8") as f:
        schema_sql = f.read()
        
    with conn.cursor() as cur:
        cur.execute(schema_sql)
    conn.commit()
    print("Schema executed successfully.")

def clean_df(df):
    """Replace Ergast '\\N' with None (NULL in SQL)"""
    return df.replace('\\N', None).where(pd.notnull(df), None)

def load_table(conn, table_name, df, columns, conflict_col, conflict_action="DO NOTHING"):
    """Generic fast loader using execute_values with ON CONFLICT"""
    if df.empty:
        return
        
    df = clean_df(df)
    
    # Ensure dataframe columns match expected
    records = [tuple(row) for row in df[columns].to_numpy()]
    
    cols_str = ','.join(columns)
    
    if conflict_col:
        conflict_clause = f"ON CONFLICT ({conflict_col}) {conflict_action}"
    else:
        conflict_clause = "ON CONFLICT DO NOTHING" # Requires PK/Unique constraints to be defined
        
    query = f"INSERT INTO {table_name} ({cols_str}) VALUES %s {conflict_clause}"
    
    with conn.cursor() as cur:
        try:
            extras.execute_values(cur, query, records, page_size=10000)
            conn.commit()
            print(f"Loaded {len(records)} records into {table_name}")
        except Exception as e:
            conn.rollback()
            print(f"Error loading {table_name}: {e}")
            raise e

def load_database():
    try:
        conn = get_connection()
    except Exception as e:
        print(f"Failed to connect to database: {e}")
        return

    print("Connected to PostgreSQL database.")
    
    try:
        execute_schema(conn)
        
        # Load Circuits
        circuits_file = os.path.join(HISTORICAL_DIR, "circuits.csv")
        if os.path.exists(circuits_file):
            df = pd.read_csv(circuits_file)
            cols = ['circuitId', 'name', 'location', 'country', 'lat', 'lng']
            df = df.rename(columns={'circuitId': 'circuit_id', 'name': 'circuit_name', 'location': 'locality', 'lat': 'latitude', 'lng': 'longitude'})
            load_table(conn, 'circuits', df, ['circuit_id', 'circuit_name', 'locality', 'country', 'latitude', 'longitude'], 'circuit_id')

        # Load Drivers
        drivers_file = os.path.join(HISTORICAL_DIR, "drivers.csv")
        if os.path.exists(drivers_file):
            df = pd.read_csv(drivers_file)
            df = df.rename(columns={'driverId': 'driver_id', 'code': 'driver_code', 'forename': 'first_name', 'surname': 'last_name', 'dob': 'date_of_birth', 'number': 'permanent_number'})
            load_table(conn, 'drivers', df, ['driver_id', 'driver_code', 'first_name', 'last_name', 'date_of_birth', 'nationality', 'permanent_number'], 'driver_id')

        # Load Constructors
        constructors_file = os.path.join(HISTORICAL_DIR, "constructors.csv")
        if os.path.exists(constructors_file):
            df = pd.read_csv(constructors_file)
            df = df.rename(columns={'constructorId': 'constructor_id', 'name': 'constructor_name'})
            load_table(conn, 'constructors', df, ['constructor_id', 'constructor_name', 'nationality'], 'constructor_id')

        # Load Races
        races_file = os.path.join(HISTORICAL_DIR, "races.csv")
        if os.path.exists(races_file):
            df = pd.read_csv(races_file)
            df = df.rename(columns={'raceId': 'race_id', 'year': 'season', 'circuitId': 'circuit_id', 'name': 'race_name', 'date': 'race_date', 'time': 'race_time'})
            load_table(conn, 'races', df, ['race_id', 'season', 'round', 'circuit_id', 'race_name', 'race_date', 'race_time'], 'race_id')

        # Load Results
        results_file = os.path.join(HISTORICAL_DIR, "results.csv")
        if os.path.exists(results_file):
            df = pd.read_csv(results_file, low_memory=False)
            df = clean_df(df)
            df = df.rename(columns={
                'resultId': 'result_id', 'raceId': 'race_id', 'driverId': 'driver_id', 
                'constructorId': 'constructor_id', 'grid': 'grid_position', 
                'positionOrder': 'finish_position', 'statusId': 'status', # Using statusId as a proxy for status string for now
                'milliseconds': 'race_time_ms', 'fastestLap': 'fastest_lap', 'rank': 'fastest_lap_rank',
                'laps': 'laps_completed'
            })
            load_table(conn, 'results', df, ['result_id', 'race_id', 'driver_id', 'constructor_id', 'grid_position', 'finish_position', 'points', 'laps_completed', 'status', 'race_time_ms', 'fastest_lap', 'fastest_lap_rank'], 'result_id')

        # Load Pit Stops
        pitstops_file = os.path.join(HISTORICAL_DIR, "pit_stops.csv")
        if os.path.exists(pitstops_file):
            df = pd.read_csv(pitstops_file)
            df = df.rename(columns={'raceId': 'race_id', 'driverId': 'driver_id', 'stop': 'stop_number', 'milliseconds': 'pit_duration_ms'})
            # Pit stops does not have a native ID in the CSV, we'll let postgres handle SERIAL pit_stop_id 
            # and use ON CONFLICT for the composite unique key
            conflict = "race_id, driver_id, stop_number"
            cols_str = "race_id, driver_id, lap, stop_number, pit_duration_ms"
            records = [tuple(row) for row in df[['race_id', 'driver_id', 'lap', 'stop_number', 'pit_duration_ms']].to_numpy()]
            query = f"INSERT INTO pit_stops ({cols_str}) VALUES %s ON CONFLICT ({conflict}) DO NOTHING"
            with conn.cursor() as cur:
                extras.execute_values(cur, query, records, page_size=10000)
            conn.commit()
            print(f"Loaded {len(records)} records into pit_stops")
            
        print("Data loading completed successfully.")

    except Exception as e:
        print(f"Process failed: {e}")
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    load_database()
