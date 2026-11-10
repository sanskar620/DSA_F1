from typing import Dict, Any

def generate_pit_explanation(decision_result: Dict[str, Any]) -> str:
    """
    Parses the optimization outputs to produce a human-readable explanation 
    of the Dynamic Pit-Wall's current recommendation.
    """
    
    decision = decision_result['decision']
    strat = decision_result['strategy']
    metrics = decision_result['metrics']
    reasons = decision_result['reasoning']
    
    explanation = f"### Recommendation: **{decision}**\n\n"
    explanation += f"**Target Strategy**: {strat}\n"
    explanation += f"**Robustness**: {decision_result['robustness']}\n\n"
    
    if decision_result['pit_window']:
        explanation += f"**Recommended Pit Window**: Laps {decision_result['pit_window'][0]} - {decision_result['pit_window'][1]}\n\n"
        
    explanation += "**Primary Reasons (Phase 8 Optimizer):**\n"
    for r in reasons:
        explanation += f"- {r}\n"
        
    explanation += "\n**Supporting Metrics (Phase 7 Monte Carlo):**\n"
    explanation += f"- Expected Race Time: {metrics['mean_race_time']:.1f}s\n"
    explanation += f"- Expected Finish Position: P{metrics['mean_finish_position']:.1f}\n"
    explanation += f"- Podium Probability: {metrics['podium_probability']*100:.1f}%\n"
    explanation += f"- Risk (Std Dev): {metrics['risk']:.1f}s\n"
    
    if "URGENT" in decision:
        explanation += "\n> **WARNING**: The optimal pit window is closing. Failing to pit now diverges from the statistically optimal strategy."
        
    return explanation
