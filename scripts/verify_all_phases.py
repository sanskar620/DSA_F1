import os
import json
import psycopg2
from dotenv import load_dotenv

def verify():
    print("=============================================")
    print("     F1 StrategyIQ - Phase Verification")
    print("=============================================\n")
    
    issues = []
    
    # PHASE 1: Raw Data
    print("--- PHASE 1: Data Collection ---")
    p1_files = [
        "data/Tyres weather data/f1_all.csv"
    ]
    for f in p1_files:
        if os.path.exists(f):
            print(f"[OK] Found: {f}")
        else:
            print(f"[MISSING] {f}")
            issues.append(f"Phase 1: Missing {f}")
            
    # PHASE 2: Database
    print("\n--- PHASE 2: PostgreSQL Database ---")
    load_dotenv(".env")
    try:
        conn = psycopg2.connect(
            host=os.getenv("DATABASE_HOST", "localhost"),
            port=os.getenv("DATABASE_PORT", "5432"),
            dbname=os.getenv("DATABASE_NAME", "f1_strategyiq"),
            user=os.getenv("DATABASE_USER", "postgres"),
            password=os.getenv("DATABASE_PASSWORD", "postgres")
        )
        cur = conn.cursor()
        cur.execute("SELECT count(*) FROM results;")
        count = cur.fetchone()[0]
        print(f"[OK] Connected to f1_strategyiq")
        print(f"[OK] 'results' table contains {count} rows")
        conn.close()
    except Exception as e:
        print(f"[ERROR] Database Error: {e}")
        issues.append(f"Phase 2: DB Connection failed ({e})")
        
    # PHASE 3: ML Features
    print("\n--- PHASE 3: Data Cleaning & Feature Engineering ---")
    p3_files = [
        "data/processed/clean_race_data.parquet",
        "data/processed/clean_lap_data.parquet",
        "data/processed/ml_features.parquet",
        "docs/feature_dictionary.md"
    ]
    for f in p3_files:
        if os.path.exists(f):
            print(f"[OK] Found: {f}")
        else:
            print(f"[MISSING] {f}")
            issues.append(f"Phase 3: Missing {f}")
            
    # PHASE 4: EDA
    print("\n--- PHASE 4: Exploratory Data Analysis ---")
    p4_files = [
        "notebooks/phase4_eda.ipynb",
        "docs/phase4_eda_report.md",
        "analysis/figures/compound_usage.png"
    ]
    for f in p4_files:
        if os.path.exists(f):
            print(f"[OK] Found: {f}")
        else:
            print(f"[MISSING] {f}")
            issues.append(f"Phase 4: Missing {f}")
            
    # PHASE 5: Machine Learning
    print("\n--- PHASE 5: Machine Learning ---")
    p5_files = [
        "models/v1/lap_time_model.joblib",
        "models/v1/lap_time_features.joblib",
        "models/v1/tyre_model.joblib",
        "models/v1/tyre_features.joblib",
        "models/v1/pit_decision_model.joblib",
        "models/v1/pit_decision_features.joblib",
        "models/v1/model_metadata.json",
        "reports/phase5_ml_report.md",
        "data/processed/model_results/lap_time_model_results.csv"
    ]
    for f in p5_files:
        if os.path.exists(f):
            print(f"[OK] Found: {f}")
        else:
            print(f"[MISSING] {f}")
            issues.append(f"Phase 5: Missing {f}")
            
    # Read Metadata if it exists
    if os.path.exists("models/v1/model_metadata.json"):
        with open("models/v1/model_metadata.json", "r") as f:
            try:
                meta = json.load(f)
                print(f"[OK] Loaded Metadata: Version {meta.get('version')} trained on {meta.get('train_races_count')} races.")
            except Exception as e:
                print(f"[ERROR] Failed to parse metadata JSON: {e}")
                issues.append("Phase 5: Invalid metadata JSON")
                
    print("\n=============================================")
    if not issues:
        print("[SUCCESS] ALL PHASES VERIFIED SUCCESSFULLY. Ready for Phase 6.")
    else:
        print(f"[WARNING] Found {len(issues)} missing/broken components:")
        for iss in issues:
            print(f"   - {iss}")

if __name__ == "__main__":
    verify()
