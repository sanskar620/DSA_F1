import pandas as pd

def extract_risk_metric(df_monte_carlo_summary: pd.DataFrame) -> pd.Series:
    """
    Extracts the primary risk penalty from the Phase 7 summary.
    
    As per Phase 8 design choices, the primary risk metric is the 
    Standard Deviation of Race Time. It is a continuous, directly interpretable 
    measure of outcome variability.
    
    This does NOT capture all forms of strategic risk, but is a proxy 
    for race-time outcome variability.
    """
    if 'Std Race Time' not in df_monte_carlo_summary.columns:
        if 'Risk (Time Std)' in df_monte_carlo_summary.columns:
            return df_monte_carlo_summary['Risk (Time Std)']
        raise ValueError("Phase 7 Monte Carlo results must contain 'Std Race Time'.")
        
    return df_monte_carlo_summary['Std Race Time']
