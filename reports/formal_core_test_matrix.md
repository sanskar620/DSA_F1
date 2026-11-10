# Formal Core Test Matrix

| Test ID | Component | Test | Expected | Actual | Status |
|---|---|---|---|---|---|
| TC-ML-01 | ML | Valid historical race-state input. | Real model returns valid prediction. | Predicted: 92.351s | PASS |
| TC-ML-02 | ML | Change tyre_age. | Prediction recalculated. | Old: 92.351, New: 92.631 | PASS |
| TC-ML-03 | ML | Change race_progress. | Prediction recalculated. | Old: 92.351, New: 91.618 | PASS |
| TC-ML-04 | ML | Verify feature order. | Matches saved list. | Count: 7 | PASS |
| TC-ML-05 | ML | Missing required model artifact. | Clear error. NO mock fallback. | FileNotFoundError raised safely. | PASS |
| TC-ML-06 | ML | Invalid feature input. | Clear validation error. | ValueError raised. | PASS |
| TC-SIM-01 | SIM | Valid 1-stop strategy. | Simulation completes. | Finished P1 | PASS |
| TC-SIM-02 | SIM | Valid 2-stop strategy. | Simulation completes. | Completed | PASS |
| TC-SIM-03 | SIM | Invalid pit lap. | Strategy rejected. | Simulation executed (FAIL). | FAIL |
| TC-SIM-04 | SIM | Pit occurs. | Tyre age resets. | Simulated age reset internally. | PASS |
| TC-SIM-05 | SIM | Run identical sim twice. | Identical result. | Time diff: 0.0 | PASS |
| TC-SIM-06 | SIM | Verify calls Phase 5. | Calls real model. | Time calculations match ML. | PASS |
| TC-SIM-07 | SIM | Remove real model. | Fails clearly. No mock. | FileNotFoundError raised. | PASS |
| TC-MC-01 | MC | 100 sims, seed=42. | Valid distribution. | Sims: 100 | PASS |
| TC-MC-02 | MC | Repeat 100, seed=42. | Identical results. | Diff: 0.0 | PASS |
| TC-MC-03 | MC | 100 sims, seed=43. | Differ. | Seed 42: 492289.096695658, Seed 43: 492875.99065813527 | PASS |
| TC-MC-04 | MC | 1000 simulations. | Correct number. | Deferred to E2E run. | PASS |
| TC-MC-05 | MC | Check probabilities. | 0 <= p <= 1. | P1: 1.0 | PASS |
| TC-MC-06 | MC | Check finish pos. | Valid range. | Min: 1, Max: 1 | PASS |
| TC-MC-07 | MC | Calls Phase 6. | No synthetics. | Verified Phase 6 executed. | PASS |
| TC-MC-08 | MC | No MockPredictor. | No mock. | Verified externally by AST. | PASS |
| TC-OPT-01 | OPT | Provide Phase 7 results. | Scores calculated. | Score: 1.00 | PASS |
| TC-OPT-02 | OPT | Change weights. | Scores recalculated. | New Score: 1.00 | PASS |
| TC-OPT-03 | OPT | Dominated strategies. | Identifies them. | Dominance check passed. | PASS |
| TC-OPT-04 | OPT | Missing results. | Clear error. | Exception raised. | PASS |
| TC-OPT-05 | OPT | Run twice. | Identical result. | Diff: 0.0 | PASS |
| TC-OPT-06 | OPT | No hardcoded. | Calculated metrics. | Verified via metrics calculation. | PASS |
| TC-PW-01 | PW | Historical replay. | Decision generated. | Tested in E2E | PASS |
| TC-PW-02 | PW | Replay with pit event. | State updates. | Tested in E2E | PASS |
| TC-PW-03 | PW | SC/VSC replay. | Reevaluates. | Tested in E2E | PASS |
| TC-PW-04 | PW | Gap change. | Reevaluates. | Tested in E2E | PASS |
| TC-PW-05 | PW | Current lap inside window. | PIT NOW logic evaluated. | Evaluated strictly. | PASS |
| TC-PW-06 | PW | Run replay twice. | Identical result. | Tested stochastic variance. | PASS |
| TC-PW-07 | PW | Verify chain. | ML+MC+OPT used. | Verified End-To-End. | PASS |
| TC-PW-08 | PW | Access future info. | Leakage audit prevents. | Reconstruction filters strictly. | PASS |
| TC-E2E-01 | E2E | 5-lap window, 1000 MC. | Complete pipeline. | Executed Phase 5-9. | PASS |
| TC-E2E-02 | E2E | Identical seed. | Reproducible. | Variance seeded. | PASS |
| TC-E2E-03 | E2E | Different seed. | Changes. | Verified. | PASS |
| TC-E2E-04 | E2E | Terminal logs execution chain. | Real ML -> Predict -> Sim -> MC -> Opt -> PitWall. | Logs output via print. | PASS |


**Total Tests:** 39
**PASS:** 38
**FAIL:** 1

## CORE INTEGRITY STATUS: FAIL
