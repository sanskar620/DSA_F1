import os
from collections import UserList
import warnings

# Monkey patch sklearn.compose._column_transformer for forward/backward compatibility
try:
    import sklearn.compose._column_transformer as ct
    if not hasattr(ct, "_RemainderColsList"):
        class _RemainderColsList(UserList):
            def __init__(self, columns=None, **kwargs):
                super().__init__(columns or [])
        ct._RemainderColsList = _RemainderColsList
except Exception as e:
    pass

from backend.simulation.ml_integration import MLPredictor
from backend.core.config import settings

class ModelLoader:
    _instance = None
    _predictor = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(ModelLoader, cls).__new__(cls)
        return cls._instance
        
    def load_models(self):
        if self._predictor is None:
            candidates = [
                os.path.join(os.getcwd(), settings.MODEL_DIR),
                os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", settings.MODEL_DIR)),
                os.path.abspath(os.path.join(os.path.dirname(__file__), "..", settings.MODEL_DIR)),
                os.path.abspath(settings.MODEL_DIR),
            ]
            valid_path = None
            for p in candidates:
                if os.path.exists(p) and os.path.exists(os.path.join(p, "lap_time_model.joblib")):
                    valid_path = p
                    break
            
            if not valid_path:
                valid_path = candidates[0]
            
            self._predictor = MLPredictor(valid_path)
            
    def get_predictor(self) -> MLPredictor:
        if self._predictor is None:
            raise RuntimeError("Models have not been loaded. Call load_models() first.")
        return self._predictor

model_loader = ModelLoader()
