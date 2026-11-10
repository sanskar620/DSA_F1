# Feature Dictionary

| Feature | Description | Type | Unit | Source | Leakage Safe? |
|---------|-------------|------|------|--------|---------------|
| raceId | Unique Race ID | Identifier | - | Database | YES |
| driverId | Unique Driver ID | Identifier | - | Database | YES |
| LapNumber | Current Lap Number | Numeric | laps | Telemetry | YES |
| position | Driver's track position | Numeric | rank | Telemetry | YES |
| lap_time_seconds | Target Variable: Time taken to complete the lap | Numeric | seconds | Telemetry | N/A (TARGET) |
| compound | Standardized Tyre Compound (SOFT, MEDIUM, HARD, etc.) | Categorical | - | Telemetry | YES |
| tyre_age | Laps completed on current tyre | Numeric | laps | Telemetry | YES |
| Stint | Current tyre stint number | Numeric | count | Telemetry | YES |
| recent_pace | Rolling mean of the PREVIOUS 3 laps | Numeric | seconds | Derived | YES (Shifted by 1) |
| pace_trend | Difference between last lap and recent_pace | Numeric | seconds | Derived | YES (Shifted by 1) |
| laps_remaining | Laps left in the race | Numeric | laps | Derived | YES |
| race_progress | Fraction of race completed (0.0 to 1.0) | Numeric | ratio | Derived | YES |
| AirTemp | Ambient Air Temperature | Numeric | °C | Weather | YES |
| TrackTemp | Track Surface Temperature | Numeric | °C | Weather | YES |
| Rainfall | Rainfall indicator / intensity | Numeric | bool/mm | Weather | YES |

> [!IMPORTANT]
> **Leakage Prevention applied:** `recent_pace` and `pace_trend` are strictly calculated using `.shift(1)`. When predicting the lap time for Lap `N`, the model only has access to the pace history up to Lap `N-1`.
