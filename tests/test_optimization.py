import pytest
import pandas as pd
import numpy as np

from backend.optimization.normalization import min_max_normalize
from backend.optimization.objective import ObjectiveWeights, get_weights
from backend.optimization.pareto import identify_pareto_front
from backend.optimization.validation import identify_baseline_strategy

def test_normalization():
    s = pd.Series([100, 150, 200])
    
    # Lower is better (e.g. Race Time)
    norm = min_max_normalize(s, lower_is_better=True)
    assert norm.iloc[0] == 1.0  # 100 is best
    assert norm.iloc[2] == 0.0  # 200 is worst
    assert norm.iloc[1] == 0.5
    
    # Higher is better (e.g. Probability)
    s2 = pd.Series([0.1, 0.5, 0.9])
    norm2 = min_max_normalize(s2, lower_is_better=False)
    assert norm2.iloc[0] == 0.0 # 0.1 is worst
    assert norm2.iloc[2] == 1.0 # 0.9 is best

def test_normalization_zero_variance():
    s = pd.Series([10, 10, 10])
    norm = min_max_normalize(s)
    assert (norm == 1.0).all()

def test_weight_validation():
    # Valid
    w1 = ObjectiveWeights(0.2, 0.2, 0.2, 0.2, 0.2)
    w1.validate()
    
    # Invalid (sum != 1)
    w2 = ObjectiveWeights(0.5, 0.5, 0.5, 0.0, 0.0)
    with pytest.raises(ValueError):
        w2.validate()
        
    # Invalid (negative)
    w3 = ObjectiveWeights(1.5, -0.5, 0.0, 0.0, 0.0)
    with pytest.raises(ValueError):
        w3.validate()

def test_pareto_front():
    df = pd.DataFrame({
        'Strategy': ['A', 'B', 'C'],
        'Mean Race Time': [100, 90, 110],       # lower is better
        'Podium Probability': [0.5, 0.8, 0.2],  # higher is better
    })
    
    # B strictly dominates A and C.
    objectives = ['Mean Race Time', 'Podium Probability']
    lower = {'Mean Race Time': True, 'Podium Probability': False}
    
    dominated = identify_pareto_front(df, objectives, lower)
    assert dominated.iloc[0] == True  # A is dominated by B
    assert dominated.iloc[1] == False # B is pareto optimal
    assert dominated.iloc[2] == True  # C is dominated by B

def test_baseline_identification():
    df = pd.DataFrame({
        'Strategy': ['A', 'B', 'C'],
        'Stops': [2, 1, 1],
        'Mean Race Time': [5000, 5010, 5005]
    })
    # B and C have 1 stop. C has lower race time than B. Baseline should be C.
    baseline = identify_baseline_strategy(df)
    assert baseline == 'C'
