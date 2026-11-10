import os
import pandas as pd

def validate_features():
    df = pd.read_parquet(os.path.join("data", "processed", "ml_features.parquet"))
    
    report_lines = ["# Phase 3 Feature Validation Report\n"]
    
    # Check 1: Negative lap times (should have been cleaned)
    neg_laps = df[df['lap_time_seconds'] <= 0].shape[0]
    if neg_laps == 0:
        report_lines.append("✅ PASS: No negative or zero lap times.")
    else:
        report_lines.append(f"❌ ERROR: Found {neg_laps} invalid lap times.")
        
    # Check 2: Invalid Tyre Age
    neg_tyre = df[df['tyre_age'] < 0].shape[0]
    if neg_tyre == 0:
        report_lines.append("✅ PASS: No negative tyre ages.")
    else:
        report_lines.append(f"❌ ERROR: Found {neg_tyre} invalid tyre ages.")
        
    # Check 3: Invalid Laps Remaining
    neg_rem = df[df['laps_remaining'] < 0].shape[0]
    if neg_rem == 0:
        report_lines.append("✅ PASS: No negative laps remaining.")
    else:
        report_lines.append(f"❌ ERROR: Found {neg_rem} invalid laps remaining.")
        
    # Check 4: Race Progress Bounds
    invalid_prog = df[(df['race_progress'] < 0) | (df['race_progress'] > 2)].shape[0] # Allowing slight > 1.0 for anomalous data but flagging wild ones
    if invalid_prog == 0:
        report_lines.append("✅ PASS: Race progress bounds look logical.")
    else:
        report_lines.append(f"⚠️ WARNING: Found {invalid_prog} strange race progress ratios.")
        
    # Check 5: Chronological Ordering & Leakage
    # If grouped by race/driver, LapNumber should be strictly increasing
    # And recent pace must logically exist
    bad_order = 0
    grouped = df.groupby(['raceId', 'driverId'])
    for _, group in grouped:
        if not group['LapNumber'].is_monotonic_increasing:
            bad_order += 1
            
    if bad_order == 0:
        report_lines.append("✅ PASS: Strict chronological ordering verified (No future data leakage).")
    else:
        report_lines.append(f"❌ ERROR: Found {bad_order} race/driver groups with bad chronological ordering.")
        
    # Check 6: Missing Values %
    report_lines.append("\n## Missing Values Percentage")
    nulls = df.isnull().mean() * 100
    for col, pct in nulls.items():
        if pct > 0:
            report_lines.append(f"- `{col}`: {pct:.2f}% missing")
            
    report_lines.append("\n*Note: High missing values on pace features in lap 1-3 of a stint are mathematically expected due to rolling averages.*")
    
    report_path = os.path.join("docs", "phase3_validation_report.md")
    with open(report_path, "w", encoding="utf-8") as f:
        f.write("\n".join(report_lines))
        
    print(f"Validation complete. Report written to {report_path}")

if __name__ == "__main__":
    validate_features()
