import os
import sys
import joblib
import json
import warnings

def verify_models():
    print("========================================\nPHASE 5: ML MODEL VERIFICATION\n========================================")
    
    model_dir = "models/v1"
    
    required_files = [
        "lap_time_model.joblib",
        "tyre_model.joblib",
        "pit_decision_model.joblib",
        "lap_time_features.joblib",
        "tyre_features.joblib",
        "pit_decision_features.joblib",
        "model_metadata.json"
    ]
    
    # Check File Existence
    for file in required_files:
        path = os.path.join(model_dir, file)
        if not os.path.exists(path):
            print(f"[FAIL] Missing required artifact: {file}")
            sys.exit(1)
        print(f"[PASS] Found: {file}")
            
    print("\n--- MODEL ORIGIN & METADATA ---")
    with open(os.path.join(model_dir, "model_metadata.json"), "r") as f:
        meta = json.load(f)
        
    print(f"Origin Pipeline: Phase 5 Kaggle Notebook")
    print(f"Algorithm: {meta.get('algorithm', 'Unknown')}")
    print(f"Framework: {meta.get('framework', 'Unknown')}")
    print(f"Creation Date: {meta.get('timestamp', 'Unknown')}")
    
    # Actually Load Models
    print("\n--- LAP-TIME PREDICTOR ---")
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        lt_model = joblib.load(os.path.join(model_dir, "lap_time_model.joblib"))
        lt_feats = joblib.load(os.path.join(model_dir, "lap_time_features.joblib"))
        
    print(f"Model Class: {type(lt_model).__name__}")
    print(f"Features ({len(lt_feats)}): {', '.join(lt_feats[:5])}... etc")
    
    print("\n--- TYRE MODEL ---")
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        tyre_model = joblib.load(os.path.join(model_dir, "tyre_model.joblib"))
        tyre_feats = joblib.load(os.path.join(model_dir, "tyre_features.joblib"))
        
    print(f"Model Class: {type(tyre_model).__name__}")
    print(f"Features ({len(tyre_feats)}): {', '.join(tyre_feats[:5])}... etc")
    
    print("\n--- PIT DECISION CLASSIFIER ---")
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        pit_model = joblib.load(os.path.join(model_dir, "pit_decision_model.joblib"))
        pit_feats = joblib.load(os.path.join(model_dir, "pit_decision_features.joblib"))
        
    print(f"Model Class: {type(pit_model).__name__}")
    print(f"Features ({len(pit_feats)}): {', '.join(pit_feats[:5])}... etc")

if __name__ == "__main__":
    verify_models()
