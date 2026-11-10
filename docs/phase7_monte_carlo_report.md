# Phase 7: Monte Carlo Strategy Simulation

## 1. Objective
The objective of Phase 7 is to extend the deterministic Race Strategy Simulator created in Phase 6 into a robust Monte Carlo simulation engine. By evaluating thousands of stochastic simulations based on historically derived uncertainty, we calculate outcome distributions and strategy risk metrics without duplicating the core race logic.

## 2. Why Monte Carlo is Needed
Deterministic simulation answers "what happens if everything goes exactly as predicted." However, Formula 1 is inherently uncertain. Minor lap-time variances, competitor pace fluctuations, and pit-stop errors compound over 50+ laps. The Monte Carlo engine repeatedly queries the deterministic model under varying realistic conditions to answer "what is the *probability* of success (e.g., Podium, P1) and the associated risk."

## 3. Phase 6 Integration
To strictly avoid code duplication and logic drift, Phase 7 utilizes Dependency Injection wrappers (`StochasticPredictor`, `StochasticCompetitorModel`). These classes wrap the deterministic Phase 6 modules, injecting controlled pseudo-random noise immediately before handing the parameters to the unaltered `simulate_strategy` loop. 

## 4. Number of Simulations
The default number of simulations is **1000** per strategy. This balances computational efficiency with statistical stability. The number is configurable via the `run_monte_carlo` parameters.

## 5. Random Seed
Reproducibility is enforced. The engine initializes a `numpy.random.Generator` using a configurable `random_seed` (default: 42). Simulating the same initial state, strategy, and config with the same seed will yield identical results, allowing fair and controlled strategy comparisons.

## 6. Uncertainty Sources
Uncertainty is explicitly configured via the `UncertaintyConfig` dataclass and injected into specific points of the simulation loop. 

## 7. Lap-Time Error Methodology
Instead of inventing an arbitrary standard deviation, the engine calculates empirical residuals from the historical validation data:
`residual = actual_lap_time - Phase_5_predicted_lap_time`
The standard deviation of these residuals dictates the normal distribution from which lap-time noise is sampled. This ensures our primary source of uncertainty is directly correlated with the real-world predictive performance of our ML models.

## 8. Competitor Uncertainty
Competitor pace variance is injected by sampling a small noise value and modifying the competitors' initial `recent_pace`. The CompetitorModel then organically advances their cumulative time using this perturbed pace throughout the race.

## 9. Pit-Stop Uncertainty
A stochastic function is passed to the Phase 6 simulator, allowing pit-loss to vary around the historical circuit average based on a configurable standard deviation (e.g., ~1.2s), simulating minor human errors or exceptional stops.

## 10. Tyre Uncertainty (No Double Counting)
Because Model 1 (Lap Time Prediction) inherently incorporates `tyre_age` and `race_progress`, tyre degradation is already captured in the baseline predictions. Additional random tyre degradation is explicitly avoided to prevent double-counting. 

## 11. Safety Car/VSC Methodology
Safety Cars and VSCs are handled strictly via a Scenario-Based approach (e.g., Green Flag vs SC on Lap X) passed via the `UncertaintyConfig`. When triggered, they apply deterministic pace penalties (e.g., 40% slower for SC) for the specified duration. We do not invent arbitrary probabilities for SC occurrences.

## 12. Weather Methodology
Similar to Safety Cars, weather acts as a static scenario configuration parameter. The current engine evaluates Monte Carlo strategies under known weather conditions to prevent inventing statistically unreliable rainfall distributions.

## 13. Output Metrics
The engine aggregates all simulations to produce:
- **Time Metrics**: Mean, Median, Min, Max, Standard Deviation, 5th, and 95th Percentile Race Time.
- **Position Metrics**: Mean, Median, Worst Finish Position.
- **Probabilities**: P1, Podium, Top-5, Top-10.
- **Risk Metrics**: Standard Deviation of Race Time (used as a primary risk indicator).

## 14. Historical Validation & Model Dependencies
**CRITICAL**: The Monte Carlo engine fundamentally relies on the actual Kaggle-trained ML artifacts (`models/v1/lap_time_model.joblib`) to estimate empirical residuals. If there is an environment mismatch (e.g., `scikit-learn` version discrepancies), the simulation will explicitly halt to prevent the silent usage of inaccurate mock models.

## 15. How Phase 8 will consume these results
Phase 7 evaluates and reports; it does not choose. The resulting probability distributions and risk metrics stored in `strategy_summary.csv` will be consumed by the Phase 8 Optimization Engine, which will apply strategic weights (e.g., Risk Tolerance vs Maximum Expected Position) to determine the mathematically optimal strategy.
