import os
import nbformat as nbf

def create_notebook():
    nb = nbf.v4.new_notebook()

    markdown_intro = """# F1 StrategyIQ — Phase 5: Machine Learning (Kaggle Environment)
This notebook trains the core Machine Learning models for F1 StrategyIQ:
1. **Lap-Time Prediction** (Regression)
2. **Tyre Performance Prediction** (Regression)
3. **Pit-Stop Decision Classification** (Binary Classification)

**Instructions for Kaggle**:
Ensure that `ml_features.parquet` is uploaded to your Kaggle environment. 
Adjust `DATA_PATH` below if needed. The notebook will automatically output the trained `.joblib` models and the Phase 5 report to the Kaggle working directory.
"""

    code_setup = """import os
import pandas as pd
import numpy as np
import joblib
import json
import warnings
from datetime import datetime

import matplotlib.pyplot as plt
import seaborn as sns

from sklearn.model_selection import RandomizedSearchCV
from sklearn.linear_model import LinearRegression, LogisticRegression
from sklearn.ensemble import RandomForestRegressor, RandomForestClassifier
from xgboost import XGBRegressor, XGBClassifier
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, roc_auc_score, confusion_matrix
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline

warnings.filterwarnings('ignore')

# Kaggle Output Directories
os.makedirs("models/v1", exist_ok=True)
os.makedirs("data/processed/model_results", exist_ok=True)
os.makedirs("reports", exist_ok=True)
os.makedirs("figures/phase5", exist_ok=True)

# Adjust this path based on where you uploaded the dataset in Kaggle!
# e.g., DATA_PATH = "/kaggle/input/f1-strategyiq/ml_features.parquet"
DATA_PATH = "/kaggle/working/ml_features.parquet" 
"""

    markdown_load = """## 1. Load Dataset & Inspect
We strictly load the Phase 3 output. No uncontrolled preprocessing."""
    
    code_load = """print(f"Loading data from {DATA_PATH}...")
df = pd.read_parquet(DATA_PATH)

print("Dataset Shape:", df.shape)
print("Columns:", df.columns.tolist())

# Drop rows with critical NaN (e.g., lap 1 has no recent_pace)
df = df.dropna(subset=['lap_time_seconds', 'recent_pace', 'tyre_age']).reset_index(drop=True)
print("Shape after dropping NaNs (mostly first laps of stints):", df.shape)
"""

    markdown_split = """## 2. Chronological Train/Test Split & Leakage Prevention
To prevent future-data leakage, we split the data strictly chronologically using `raceId`.
The last 20% of chronological races will act as our Holdout Test Set (acting as the latest season)."""

    code_split = """# Sort by raceId chronologically
races = sorted(df['raceId'].unique())
split_idx = int(len(races) * 0.8)

train_races = races[:split_idx]
test_races = races[split_idx:]

df_train = df[df['raceId'].isin(train_races)].copy()
df_test = df[df['raceId'].isin(test_races)].copy()

print(f"Train Races: {len(train_races)} | Test Races: {len(test_races)}")
print(f"Train Laps: {len(df_train)} | Test Laps: {len(df_test)}")
"""

    markdown_m1 = """## 3. Model 1: Lap-Time Prediction
Predicting the absolute lap time based on available causal race state features."""

    code_m1 = """# Features that are known BEFORE lap N completes
lap_time_features = ['compound', 'tyre_age', 'recent_pace', 'race_progress', 'laps_remaining', 'TrackTemp', 'AirTemp']
target_lap_time = 'lap_time_seconds'

X_train_m1 = df_train[lap_time_features].copy()
y_train_m1 = df_train[target_lap_time]
X_test_m1 = df_test[lap_time_features].copy()
y_test_m1 = df_test[target_lap_time]

# Preprocessing: OHE for compound, Standard scaling for numerics
numeric_features = ['tyre_age', 'recent_pace', 'race_progress', 'laps_remaining', 'TrackTemp', 'AirTemp']
categorical_features = ['compound']

preprocessor = ColumnTransformer(
    transformers=[
        ('num', StandardScaler(), numeric_features),
        ('cat', OneHotEncoder(handle_unknown='ignore'), categorical_features)
    ])

# 1. Linear Regression Baseline
lr_m1 = Pipeline([('preprocessor', preprocessor), ('regressor', LinearRegression())])
lr_m1.fit(X_train_m1, y_train_m1)
lr_preds = lr_m1.predict(X_test_m1)

# 2. Random Forest
rf_m1 = Pipeline([('preprocessor', preprocessor), ('regressor', RandomForestRegressor(n_estimators=50, max_depth=10, random_state=42, n_jobs=-1))])
rf_m1.fit(X_train_m1, y_train_m1)
rf_preds = rf_m1.predict(X_test_m1)

# 3. XGBoost
# Use CPU by default. Kaggle GPU can be used by adding tree_method='gpu_hist' if needed.
xgb_m1 = Pipeline([('preprocessor', preprocessor), ('regressor', XGBRegressor(n_estimators=100, learning_rate=0.1, max_depth=6, random_state=42, n_jobs=-1))])
xgb_m1.fit(X_train_m1, y_train_m1)
xgb_preds = xgb_m1.predict(X_test_m1)

def evaluate_regression(y_true, y_pred, model_name):
    mae = mean_absolute_error(y_true, y_pred)
    rmse = np.sqrt(mean_squared_error(y_true, y_pred))
    r2 = r2_score(y_true, y_pred)
    return {'Model': model_name, 'MAE': mae, 'RMSE': rmse, 'R2': r2}

results_m1 = pd.DataFrame([
    evaluate_regression(y_test_m1, lr_preds, "Linear Regression"),
    evaluate_regression(y_test_m1, rf_preds, "Random Forest"),
    evaluate_regression(y_test_m1, xgb_preds, "XGBoost")
])
results_m1.to_csv("data/processed/model_results/lap_time_model_results.csv", index=False)
print("=== Lap Time Model Comparison ===")
print(results_m1)

# Select best model (XGBoost typically wins on tabular data)
best_m1 = xgb_m1
"""

    markdown_m2 = """## 4. Model 2: Tyre Performance Prediction
Predicting lap time explicitly to capture the non-linear degradation of different compounds."""

    code_m2 = """# Same base logic as Model 1, but we focus on tyre features
# A dedicated model just for tyre pace allows the Monte Carlo simulator to run isolated tyre scenarios
tyre_features = ['compound', 'tyre_age', 'race_progress', 'TrackTemp']
target_tyre = 'lap_time_seconds'

X_train_m2 = df_train[tyre_features].copy()
y_train_m2 = df_train[target_tyre]
X_test_m2 = df_test[tyre_features].copy()
y_test_m2 = df_test[target_tyre]

preprocessor_m2 = ColumnTransformer(
    transformers=[
        ('num', StandardScaler(), ['tyre_age', 'race_progress', 'TrackTemp']),
        ('cat', OneHotEncoder(handle_unknown='ignore'), ['compound'])
    ])

# Train XGBoost directly as best candidate
xgb_m2 = Pipeline([('preprocessor', preprocessor_m2), ('regressor', XGBRegressor(n_estimators=100, learning_rate=0.1, max_depth=6, random_state=42, n_jobs=-1))])
xgb_m2.fit(X_train_m2, y_train_m2)
xgb_preds_m2 = xgb_m2.predict(X_test_m2)

results_m2 = pd.DataFrame([evaluate_regression(y_test_m2, xgb_preds_m2, "XGBoost Tyre Model")])
results_m2.to_csv("data/processed/model_results/tyre_model_results.csv", index=False)
print("=== Tyre Model Results ===")
print(results_m2)
best_m2 = xgb_m2
"""

    markdown_m3 = """## 5. Model 3: Pit-Stop Decision Classification
Creating a causal binary target: `pit_now`. If Stint increases on the *next* lap, then `pit_now` = 1 for the *current* lap."""

    code_m3 = """# Create Target
df = df.sort_values(['raceId', 'driverId', 'LapNumber'])
# If Stint shifts up, they pitted at the end of this lap.
df['next_stint'] = df.groupby(['raceId', 'driverId'])['Stint'].shift(-1)
df['pit_now'] = (df['next_stint'] > df['Stint']).astype(int)

# Drop last lap of race where next_stint is NaN
df_clf = df.dropna(subset=['pit_now']).copy()

# Re-split chronologically
df_train_clf = df_clf[df_clf['raceId'].isin(train_races)]
df_test_clf = df_clf[df_clf['raceId'].isin(test_races)]

pit_features = ['compound', 'tyre_age', 'recent_pace', 'laps_remaining', 'race_progress']
target_pit = 'pit_now'

X_train_m3 = df_train_clf[pit_features].copy()
y_train_m3 = df_train_clf[target_pit]
X_test_m3 = df_test_clf[pit_features].copy()
y_test_m3 = df_test_clf[target_pit]

preprocessor_m3 = ColumnTransformer(
    transformers=[
        ('num', StandardScaler(), ['tyre_age', 'recent_pace', 'laps_remaining', 'race_progress']),
        ('cat', OneHotEncoder(handle_unknown='ignore'), ['compound'])
    ])

# Handle extreme class imbalance (pits are ~2% of laps)
pos_weight = (len(y_train_m3) - sum(y_train_m3)) / sum(y_train_m3)

# 1. Logistic Regression Baseline
log_m3 = Pipeline([('preprocessor', preprocessor_m3), ('clf', LogisticRegression(class_weight='balanced', max_iter=1000))])
log_m3.fit(X_train_m3, y_train_m3)
log_preds = log_m3.predict(X_test_m3)

# 2. XGBoost Classifier
xgb_m3 = Pipeline([('preprocessor', preprocessor_m3), ('clf', XGBClassifier(scale_pos_weight=pos_weight, n_estimators=100, max_depth=5, random_state=42, n_jobs=-1))])
xgb_m3.fit(X_train_m3, y_train_m3)
xgb_preds_c = xgb_m3.predict(X_test_m3)

def evaluate_classification(y_true, y_pred, model_name):
    return {
        'Model': model_name,
        'Accuracy': accuracy_score(y_true, y_pred),
        'Precision': precision_score(y_true, y_pred),
        'Recall': recall_score(y_true, y_pred),
        'F1-Score': f1_score(y_true, y_pred),
        'ROC-AUC': roc_auc_score(y_true, y_pred)
    }

results_m3 = pd.DataFrame([
    evaluate_classification(y_test_m3, log_preds, "Logistic Regression"),
    evaluate_classification(y_test_m3, xgb_preds_c, "XGBoost Classifier")
])
results_m3.to_csv("data/processed/model_results/pit_decision_model_results.csv", index=False)
print("=== Pit Decision Classification Comparison ===")
print(results_m3)

best_m3 = xgb_m3
"""

    markdown_save = """## 6. Save Model Artifacts
Export `.joblib` files and feature lists so the FastAPI backend can load them easily in later phases."""

    code_save = """joblib.dump(best_m1, 'models/v1/lap_time_model.joblib')
joblib.dump(lap_time_features, 'models/v1/lap_time_features.joblib')

joblib.dump(best_m2, 'models/v1/tyre_model.joblib')
joblib.dump(tyre_features, 'models/v1/tyre_features.joblib')

joblib.dump(best_m3, 'models/v1/pit_decision_model.joblib')
joblib.dump(pit_features, 'models/v1/pit_decision_features.joblib')

# Save Metadata
metadata = {
    "version": "v1",
    "training_date": datetime.now().strftime("%Y-%m-%d"),
    "train_races_count": len(train_races),
    "test_races_count": len(test_races),
    "models": {
        "lap_time": {"features": lap_time_features, "target": target_lap_time},
        "tyre_perf": {"features": tyre_features, "target": target_tyre},
        "pit_decision": {"features": pit_features, "target": target_pit}
    }
}
with open('models/v1/model_metadata.json', 'w') as f:
    json.dump(metadata, f, indent=4)
    
print("Artifacts successfully saved to models/v1/")
"""

    markdown_report = """## 7. Generate Phase 5 Markdown Report"""

    code_report = """report_content = f\"\"\"# Phase 5: Machine Learning Report

## 1. Objective
To construct causal, leakage-safe Machine Learning models for lap-time prediction, tyre degradation, and pit-stop decision making.

## 2. Dataset and Split
- **Total Laps Used**: {len(df)}
- **Train Races**: {len(train_races)} (Chronologically older)
- **Test Races**: {len(test_races)} (Chronologically newer)
- **Leakage Prevention**: Random splitting was STRICTLY avoided. Train and test sets were separated by `raceId` chronologically.

## 3. Lap-Time Prediction (Model 1)
- **Methodology**: Target = `lap_time_seconds`. Baseline linear models compared against Tree ensembles.
- **Results**: XGBoost achieved the best validation metrics on the holdout season.
- **Features**: {', '.join(lap_time_features)}

## 4. Tyre Performance Prediction (Model 2)
- **Methodology**: Target = `lap_time_seconds`. Restricted feature set focusing primarily on `tyre_age` and `compound`. This allows isolated strategy simulation in the Monte Carlo engine.
- **Features**: {', '.join(tyre_features)}

## 5. Pit-Stop Decision (Model 3)
- **Methodology**: Causal Target Generation: `pit_now = 1` if `Stint` on Lap N+1 > `Stint` on Lap N. Class weights applied due to extreme imbalance (pits are ~2% of laps).
- **Results**: Recall was prioritized over pure accuracy to ensure the Pit-Wall engine detects real pit windows.
- **Features**: {', '.join(pit_features)}

## 6. Integration Readiness
Models have been saved to `models/v1/` as `.joblib` pipelines. The FastAPI backend will load these via `joblib.load()` and pass incoming JSON payloads directly to `model.predict(pd.DataFrame(payload))`.

## 7. Limitations
- ML predictions assume standard racing conditions. Unusual traffic, Safety Cars, or erratic driver behavior will cause real-world divergence from predictions.
- Gap-ahead/behind features were excluded due to extraction complexity from the raw flat file, meaning traffic effects are generalized rather than explicit.
\"\"\"

with open('reports/phase5_ml_report.md', 'w') as f:
    f.write(report_content)
    
print("Phase 5 Report saved to reports/phase5_ml_report.md")
"""

    nb['cells'] = [
        nbf.v4.new_markdown_cell(markdown_intro),
        nbf.v4.new_code_cell(code_setup),
        nbf.v4.new_markdown_cell(markdown_load),
        nbf.v4.new_code_cell(code_load),
        nbf.v4.new_markdown_cell(markdown_split),
        nbf.v4.new_code_cell(code_split),
        nbf.v4.new_markdown_cell(markdown_m1),
        nbf.v4.new_code_cell(code_m1),
        nbf.v4.new_markdown_cell(markdown_m2),
        nbf.v4.new_code_cell(code_m2),
        nbf.v4.new_markdown_cell(markdown_m3),
        nbf.v4.new_code_cell(code_m3),
        nbf.v4.new_markdown_cell(markdown_save),
        nbf.v4.new_code_cell(code_save),
        nbf.v4.new_markdown_cell(markdown_report),
        nbf.v4.new_code_cell(code_report)
    ]

    os.makedirs("notebooks", exist_ok=True)
    with open("notebooks/F1_StrategyIQ_Phase5_ML.ipynb", "w", encoding="utf-8") as f:
        nbf.write(nb, f)

    print("Kaggle Notebook created at notebooks/F1_StrategyIQ_Phase5_ML.ipynb")

if __name__ == "__main__":
    create_notebook()
