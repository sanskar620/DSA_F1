# Data Dictionary & Source Mapping

This document maps the primary and backup data sources for the F1 StrategyIQ project and distinguishes between raw fields and derived features.

## Source Mapping

| Information | Primary Source | Backup Source | Type |
|--------------|----------------|---------------|------|
| Season | Historical Dataset/Jolpica | — | RAW |
| Race | Jolpica | Historical Dataset | RAW |
| Driver | Jolpica | Historical Dataset | RAW |
| Constructor | Jolpica | Historical Dataset | RAW |
| Race Result | Jolpica | Historical Dataset | RAW |
| Championship Standings | Jolpica | Historical Dataset | RAW |
| Pit Stops | Jolpica/FastF1 | Historical Dataset | RAW |
| Lap Time | FastF1 | Weather/Tyre Dataset | RAW |
| Tyre Compound | FastF1 | Weather/Tyre Dataset | RAW |
| Tyre Age | Derived/FastF1 | Weather/Tyre Dataset | DERIVED |
| Weather | FastF1 | Weather/Tyre Dataset | RAW |
| Track Temperature | FastF1 | Weather/Tyre Dataset | RAW |
| Track Status | FastF1 | — | RAW |
| Sector Times | FastF1 | — | RAW |
| Telemetry | FastF1 | — | RAW |
| Degradation Rate | Derived (ML) | — | DERIVED |

## Notes
- **Raw Fields:** Fields directly extracted from Jolpica API, FastF1, or historical CSV datasets.
- **Derived Fields:** Fields that require computation (e.g., Tyre Age calculated from lap counts minus pit stops, or degradation rates from ML models). These are computed dynamically in Phase 2 or Phase 3.
- Do not assume every field is perfectly available in all races (e.g., telemetry is only reliable post-2018).
