import pandas as pd

def identify_pareto_front(df: pd.DataFrame, objectives: list, lower_is_better: dict) -> pd.Series:
    """
    Identifies which strategies are Pareto-dominated.
    A strategy is dominated if another strategy is >= in all objectives 
    and strictly > in at least one objective.
    
    Returns a boolean Series (True if Dominated, False if Pareto Optimal).
    """
    is_dominated = pd.Series(False, index=df.index)
    
    # Extract just the objective columns as a numpy array for speed
    data = df[objectives].values
    
    # Flip signs so that "larger is better" for ALL columns during comparison
    for i, col in enumerate(objectives):
        if lower_is_better.get(col, True):
            data[:, i] = -data[:, i]
            
    for i in range(len(data)):
        for j in range(len(data)):
            if i == j:
                continue
            
            # Check if j dominates i
            # j is >= i in all objectives AND j is > i in at least one
            if (data[j] >= data[i]).all() and (data[j] > data[i]).any():
                is_dominated.iloc[i] = True
                break
                
    return is_dominated
