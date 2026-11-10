# Phase 10: FastAPI Backend Documentation

## Overview

The F1 StrategyIQ backend connects the deterministic and stochastic core engines to a unified, documented REST API using **FastAPI**.

## Features

- **Pydantic Validation**: All requests and responses are strictly validated.
- **Model Singleton**: Machine Learning artifacts (Phase 5) are loaded exactly once at startup via the `model_loader` singleton.
- **PostgreSQL Integration**: Real-time integration via SQLAlchemy.
- **CORS Support**: Integrated specifically for the Streamlit frontend.

## API Structure

### System

- `GET /api/health`
  Checks if models are loaded and if the PostgreSQL connection is healthy.

### ML Predictions (Phase 5)

- `POST /api/predict/lap-time`
  Predicts lap time for a given `RaceState`.
- `POST /api/predict/tyre`
  Predicts tyre degradation.
- `POST /api/predict/pit-decision`
  Returns the raw PIT NOW or STAY OUT binary classification probability.

### Strategy Engine (Phases 6, 7, 8)

- `POST /api/strategy/simulate`
  Executes a deterministic simulation for a specific strategy (Phase 6).
- `POST /api/strategy/monte-carlo`
  Executes stochastic simulations across `N` branches (Phase 7).
- `POST /api/strategy/optimize`
  Evaluates candidate strategies to maximize the `objective` (Phase 8).

### Pit-Wall Engine (Phase 9)

- `POST /api/pitwall/decision`
  Uses the live context to produce an immediate actionable Pit-Wall recommendation.
- `POST /api/pitwall/replay`
  Replays historical telemetry dynamically for E2E validation.

## Running the API

```bash
cd "e:\DSA PROJECT"
uvicorn backend.main:app --reload
```
