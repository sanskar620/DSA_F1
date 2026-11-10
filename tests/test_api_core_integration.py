from fastapi.testclient import TestClient
from backend.main import app
from backend.core.model_loader import model_loader

# Force load models for testing
try:
    model_loader.load_models()
except:
    pass

client = TestClient(app)

def test_lap_time_perturbation():
    base_request = {
        "season": 2024,
        "race_id": 1,
        "driver_id": 1,
        "lap_number": 10,
        "current_position": 1,
        "tyre_age": 5,
        "compound": "SOFT"
    }
    
    res1 = client.post("/api/predict/lap-time", json=base_request)
    assert res1.status_code == 200, res1.text
    t1 = res1.json()["predicted_lap_time"]
    
    # Perturb tyre age
    req2 = base_request.copy()
    req2["tyre_age"] = 25
    
    res2 = client.post("/api/predict/lap-time", json=req2)
    assert res2.status_code == 200, res2.text
    t2 = res2.json()["predicted_lap_time"]
    
    # Prove that the API forwards to the real model (t2 should be slower due to age)
    assert t1 != t2, "Prediction did not change despite feature perturbation! Real model may not be connected."

def test_pit_decision_call():
    req = {
        "season": 2024,
        "race_id": 1,
        "driver_id": 1,
        "lap_number": 50,
        "current_position": 1,
        "tyre_age": 30,
        "compound": "SOFT"
    }
    res = client.post("/api/predict/pit-decision", json=req)
    assert res.status_code == 200, res.text
    data = res.json()
    assert "pit_probability" in data
    assert "stay_out_probability" in data
    
    # Probabilities should be calculated by model.predict_proba()
    assert 0.0 <= data["pit_probability"] <= 1.0
