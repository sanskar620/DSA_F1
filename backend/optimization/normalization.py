import pandas as pd
import numpy as np

def min_max_normalize(series: pd.Series, lower_is_better: bool = True) -> pd.Series:
    """
    Normalizes a Pandas Series using Min-Max scaling to a [0, 1] range.
    After normalization, 1.0 ALWAYS represents the "best" outcome.
    
    If lower_is_better is True (e.g., Race Time, Finish Position):
        Best (lowest value) -> 1.0
        Worst (highest value) -> 0.0
        
    If lower_is_better is False (e.g., Podium Probability):
        Best (highest value) -> 1.0
        Worst (lowest value) -> 0.0
    """
    s_min = series.min()
    s_max = series.max()
    
    # Handle zero-variance edge case to avoid NaNs
    if np.isclose(s_min, s_max):
        return pd.Series(1.0, index=series.index)
        
    normalized = (series - s_min) / (s_max - s_min)
    
    if lower_is_better:
        return 1.0 - normalized
    else:
        return normalized
