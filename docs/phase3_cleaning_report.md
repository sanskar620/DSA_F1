# Phase 3 Data Cleaning Report

## 1. Input Tables (PostgreSQL)
- `races`: 1125 rows
- `results`: 26759 rows
- `circuits`: 77 rows

Saved `clean_race_data.parquet` with 26759 rows.

## 2. Input Tables (Telemetry CSV)
- `f1_all.csv`: 69230 rows

## 3. Cleaning Rules Applied
- **Lap Times**: Converted `milliseconds` to `lap_time_seconds`. Set impossible times (<=0 or >10m) to NaN.
  - Invalid lap times nullified: 235
- **Tyres**: Mapped 'UNKNOWN' to NaN, retained SOFT, MEDIUM, HARD, INTERMEDIATE, WET. Created `original_compound` for traceability.
- **Lap Numbers**: Removed lap numbers < 1.
  - Invalid lap records removed: 0
- **Weather Alignment**: Left as NaN where unavailable. FastF1 alignment done via timestamp `merge_asof` (backward).

## 4. Final Cleaned Dataset
- Cleaned Lap Rows: 69230
- Saved to `clean_lap_data.parquet`

## 5. Available Weather Fields
AirTemp, TrackTemp, Humidity, Pressure, WindSpeed, WindDirection, Rainfall
