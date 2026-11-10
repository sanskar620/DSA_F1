from typing import List, Dict, Any
import pandas as pd

class DecisionHistory:
    """
    Maintains a complete log of decisions made during a historical race replay.
    """
    def __init__(self):
        self.logs: List[Dict[str, Any]] = []
        
    def add_decision(self, lap: int, event_trigger: str, decision_result: Dict[str, Any]):
        log_entry = {
            "lap": lap,
            "event_trigger": event_trigger,
            "decision": decision_result['decision'],
            "recommended_compound": decision_result['recommended_compound'],
            "strategy": decision_result['strategy'],
            "objective": decision_result['objective'],
            "robustness": decision_result['robustness'],
            "expected_finish": decision_result['metrics']['mean_finish_position'],
            "podium_prob": decision_result['metrics']['podium_probability']
        }
        self.logs.append(log_entry)
        
    def to_dataframe(self) -> pd.DataFrame:
        return pd.DataFrame(self.logs)
