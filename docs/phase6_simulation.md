# Phase 6: Race Strategy Simulation

## 1. Objective
The objective of this phase is to build a deterministic lap-by-lap race simulator. The simulator evaluates strategic decisions (when to pit, what compound to take) and estimates the overall race outcome based on a given race state, using the causal Machine Learning models trained in Phase 5.

## 2. Core Architecture
The simulation engine acts as the backend orchestrator and is decoupled from FastAPI to remain modular.
- `RaceState`: Represents the exact deterministic state of the race (laps, tyres, positions, gaps).
- `Strategy`: Represents a list of planned compounds and the exact laps to pit.
- `MLPredictor`: Loads the Phase 5 `.joblib` models to predict lap-times natively.
- `RaceSimulator`: Executes the lap-by-lap state transition.

## 3. Modelling Assumptions & Methods

### Tyre Modelling & Double-Counting
We employ **Model 1 (Lap Time Prediction)** exclusively for the core pace calculation. Because Model 1 was trained with `tyre_age` and `race_progress` as features, it inherently predicts tyre degradation compounded with fuel-burn effects. Injecting a secondary degradation penalty from a separate tyre model would result in double-counting. The dedicated Tyre Model (Model 2) remains isolated for specific tyre-window API queries.

### Competitor Modeling
To estimate the strategic finishing position, competitors are simulated using a simplified constant pace assumption derived from their `recent_pace` prior to the simulation start. For Phase 6, we do not attempt a complex multi-agent simulation for competitors. We simply accumulate their lap times to establish a relative timeline against which we can place our target driver's predicted time.

### Pit-Stop Modeling
Historical circuit-specific pit lane loss is applied (fallback: ~22.0 seconds) when a pit stop occurs. A pit stop resets `tyre_age` to 0, updates the `compound`, increments the `stint`, and adds the penalty to the cumulative time.

### Fuel & Weather
- **Fuel**: Handled organically through the `race_progress` proxy feature within Model 1.
- **Weather**: Held constant for deterministic simulation. Future phases involving stochastic forecasting will inject dynamic weather into the state loop.
- **Safety Cars / VSC**: The simulator currently assumes green-flag racing. 

## 4. Execution Flow
1. Generates valid 1-stop and 2-stop strategies.
2. Clones the initial `RaceState` for each strategy.
3. For each lap: 
   - Checks if a pit stop is scheduled -> updates state.
   - Extracts the exact feature dictionary required by Model 1.
   - Predicts lap time and updates cumulative race time.
   - Estimates current position via `CompetitorModel`.
4. Outputs total race time, estimated position, and full lap-history.

## 5. Limitations
This deterministic simulator relies heavily on the quality of historical data. Significant real-world factors such as traffic (DRS trains), defensive driving, and sudden weather changes are not captured by the deterministic ML predictions. Phase 7 (Monte Carlo) will introduce probability distributions to handle these uncertainties.
