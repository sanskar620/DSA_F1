# Phase 11: React Frontend Mapping

| Frontend Page/Component | Current Data Source | Mock? | Required API | Integration Status |
|---|---|---|---|---|
| `StrategyDashboard` (Sidebar) | `races`, `drivers` arrays | YES | `GET /api/races`, `GET /api/drivers` | Pending |
| `Overview` | `getRaceData()`, `getPitwallDecision()` | YES | `GET /api/races/{id}`, `POST /api/pitwall/decision` | Pending |
| `RaceAnalysis` | `getRaceData()`, `getDriverData()` | YES | `GET /api/races/{id}`, `GET /api/drivers/{id}/performance` | Pending |
| `TyreIntelligence` | `predictTyreDegradation()` math loop | YES | `POST /api/predict/tyre` | Pending |
| `StrategyOptimizer` | `optimizeStrategy()`, `strategies` array | YES | `POST /api/strategy/optimize` | Pending |
| `PitWall` (Replay) | `getPitwallDecision()`, `getRaceData()` | YES | `POST /api/pitwall/replay` | Pending |
| `WhatIf` (Sandbox) | local `scenarios` math state | YES | `POST /api/strategy/simulate` | Pending |
