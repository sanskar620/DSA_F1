# Phase 11 Frontend to API Mapping

## Overview

The current frontend (React/Vite) relies heavily on `src/lib/mock-race.ts` to supply fabricated race telemetry, predictions, and strategy logic. This document maps these frontend features to their respective FastAPI endpoints.

---

### 1. Overview Page & Race Configuration
**UI Component**: `Overview` (Top-level metrics & Race Config)
**Current Source**: Static arrays (`races`, `drivers`, `compounds`) in `mock-race.ts`
**FastAPI Endpoint**: 
- `GET /api/races`
- `GET /api/drivers`
- `GET /api/health`
**Integration Status**: To be connected. Will fetch real database dropdowns and backend health status.

### 2. Race Analysis
**UI Component**: `RaceAnalysis` (Telemetry charts, gap trends, position trends)
**Current Source**: `getRaceData()` & `getDriverData()` (Mathematical sine-wave generation)
**FastAPI Endpoint**: 
- `GET /api/races/{race_id}`
- `GET /api/drivers/{driver_id}/performance`
**Integration Status**: To be connected. The backend needs to supply actual lap-by-lap telemetry for the charts.

### 3. Tyre Intelligence
**UI Component**: `TyreIntelligence` (Degradation curves)
**Current Source**: `predictTyreDegradation()` (Hardcoded math formula)
**FastAPI Endpoint**: 
- `POST /api/predict/tyre`
**Payload**: `LapTimeRequest` schema.
**Integration Status**: To be connected. Will use real Phase 5 Hybrid ML/Analytical model.

### 4. Strategy Optimizer
**UI Component**: `StrategyOptimizer` (Candidate tables, probabilities, race time)
**Current Source**: Static `strategies` array and `optimizeStrategy()` based on risk parameter.
**FastAPI Endpoint**: 
- `POST /api/strategy/optimize`
**Payload**: `OptimizeRequest` (Requires current race state and candidate strategies).
**Integration Status**: To be connected. Will invoke the Phase 6 Simulator, Phase 7 Monte Carlo, and Phase 8 Optimizer.

### 5. Dynamic Pit-Wall (Replay)
**UI Component**: `PitWall` (Live recommendation, window, decision history)
**Current Source**: `getPitwallDecision()` (Hardcoded rule-based thresholds)
**FastAPI Endpoint**: 
- `POST /api/pitwall/decision` (For the live recommendation)
- `POST /api/pitwall/replay` (For the historical chart)
**Payload**: Current `RaceState` context.
**Integration Status**: To be connected.

### 6. What-If Simulator
**UI Component**: `WhatIf` (Scenario testing, time penalties)
**Current Source**: Client-side math (`tyreBonus + scBonus + rainPenalty`)
**FastAPI Endpoint**: 
- `POST /api/strategy/simulate` (Deterministic)
- `POST /api/strategy/monte-carlo` (Stochastic distributions)
**Payload**: Overridden `RaceState` and target `Strategy`.
**Integration Status**: To be connected. The client-side math will be stripped entirely.
