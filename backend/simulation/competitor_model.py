from typing import List, Dict

class CompetitorModel:
    def __init__(self, competitors: List[Dict]):
        """
        Initializes competitors with their starting race time and recent pace.
        competitors: [{'driver': 'VER', 'cumulative_time': 1200.5, 'recent_pace': 91.2}, ...]
        """
        self.competitors = competitors

    def simulate_lap(self):
        """
        Advances all competitors by 1 lap using a simplified pace assumption.
        As agreed in Phase 6, we use their `recent_pace` with a slight pace adjustment.
        """
        for comp in self.competitors:
            # Simplified assumption: Competitors maintain their recent pace with minor organic fluctuation.
            # In Phase 6 we hold it mostly constant or apply a tiny fuel-burn proxy (getting faster).
            fuel_effect = -0.05 # average F1 fuel effect per lap
            
            comp['recent_pace'] += fuel_effect
            comp['cumulative_time'] += comp['recent_pace']
            
    def get_estimated_position(self, target_cumulative_time: float) -> int:
        """
        Returns the estimated track position of our target driver
        by comparing their time against the competitors.
        """
        times = [c['cumulative_time'] for c in self.competitors]
        times.append(target_cumulative_time)
        times.sort()
        
        # Position is 1-indexed based on where target_cumulative_time lands
        return times.index(target_cumulative_time) + 1
