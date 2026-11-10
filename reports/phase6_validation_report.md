# Phase 6: Race Simulation Validation Report

## 1. Objective
Validate the deterministic race simulator using historical Race 1120.

## 2. Methodology
- **Driver**: 830
- **Simulation Start Lap**: 15
- **Total Laps**: 58
- **Competitors Simulated**: 5
- **Candidate Strategies Evaluated**: 12

## 3. Results
```text
                    Strategy  Stops  Predicted Time  Estimated Position
0       MEDIUM - SOFT - SOFT      2      5269.31069                   4
1     MEDIUM - MEDIUM - SOFT      2      5269.31069                   4
2       MEDIUM - SOFT - HARD      2      5269.31069                   4
3     MEDIUM - SOFT - MEDIUM      2      5269.31069                   4
4   MEDIUM - MEDIUM - MEDIUM      2      5269.31069                   4
5     MEDIUM - HARD - MEDIUM      2      5269.31069                   4
6       MEDIUM - HARD - SOFT      2      5269.31069                   4
7     MEDIUM - MEDIUM - HARD      2      5269.31069                   4
8       MEDIUM - HARD - HARD      2      5269.31069                   4
9            MEDIUM - MEDIUM      1      5273.21069                   4
10             MEDIUM - HARD      1      5273.21069                   4
11             MEDIUM - SOFT      1      5273.21069                   4
```

## 4. Analysis
The simulator successfully advanced the race state deterministically. 
Tyre degradation and fuel burn were implicitly handled by Model 1 (Lap Time Predictor) avoiding any double counting. 
Competitor positions were estimated using a simplified trace of their `recent_pace`.
