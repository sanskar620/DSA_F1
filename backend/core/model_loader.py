import os
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
            model_path = os.path.join(os.getcwd(), settings.MODEL_DIR)
            if not os.path.exists(model_path):
                raise RuntimeError(f"MODEL_DIR '{model_path}' does not exist.")
            
            # This will fail loudly if the model files are missing
            self._predictor = MLPredictor(settings.MODEL_DIR)
            
    def get_predictor(self) -> MLPredictor:
        if self._predictor is None:
            raise RuntimeError("Models have not been loaded. Call load_models() first.")
        return self._predictor

model_loader = ModelLoader()
