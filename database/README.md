# F1 StrategyIQ Database

This directory contains the database schema and seeds for the F1 StrategyIQ PostgreSQL database.

## Data Source Tracking
We load data from multiple potential sources (Historical CSVs, Weather/Tyre CSVs, FastF1). 
Instead of adding a `source_system` string column to every single table which creates unnecessary duplication and increases table sizes, we use the following structural mapping:
- Base metadata (`circuits`, `drivers`, `constructors`, `races`, `results`, `pit_stops`) is primarily sourced from the Historical Dataset (`data/external/Historical data/`).
- Session-level telemetry and conditions (`laps`, `weather`, `tyre_stints`, `race_control`) are sourced from FastF1 APIs or the secondary Weather/Tyres dataset where applicable.

Any disputes are handled during the load phase by upserting `ON CONFLICT` and prioritizing the more granular data source (e.g., FastF1 telemetry > Historical CSVs).

## Loading Process
The loading system (`scripts/load_database.py`) uses strict transactions. If a table fails to load due to foreign key violations, the transaction is rolled back and the database state remains clean.
