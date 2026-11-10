import requests
import time
import sys
import subprocess

def run_e2e_tests():
    # 1. Start Server
    print("Starting FastAPI Server...")
    server = subprocess.Popen([sys.executable, "-m", "uvicorn", "backend.main:app", "--port", "8005"])
    
    try:
        # Wait for models to load and server to start
        time.sleep(10)
        
        base_url = "http://localhost:8005/api"
        
        # 4. Health endpoint works
        res = requests.get(f"{base_url}/health")
        assert res.status_code == 200
        health = res.json()
        print("Health:", health)
        assert health["models"] == "loaded", "Models failed to load in API"
        assert health["database"] == "connected", "PostgreSQL connection failed"
        print("[PASS] Health endpoint and PostgreSQL connected.")
        
        # 5. Real lap-time prediction
        req_lap = {
            "season": 2024, "race_id": 1, "driver_id": 1, "lap_number": 10,
            "current_position": 1, "tyre_age": 5, "compound": "SOFT"
        }
        res_lap = requests.post(f"{base_url}/predict/lap-time", json=req_lap)
        assert res_lap.status_code == 200, res_lap.text
        print(f"[PASS] Lap time prediction: {res_lap.json()['predicted_lap_time']}")
        
        # 6. Real pit classifier
        res_pit = requests.post(f"{base_url}/predict/pit-decision", json=req_lap)
        assert res_pit.status_code == 200, res_pit.text
        print(f"[PASS] Pit classifier: {res_pit.json()['decision']}")
        
        # 7. Phase 6 Simulator
        state_req = {
            "race_id": 1, "circuit": "unknown", "driver": "1", "constructor": "c",
            "current_lap": 10, "total_laps": 50, "laps_remaining": 40, "current_position": 1,
            "compound": "SOFT", "tyre_age": 5, "stint": 1, "stint_lap": 5,
            "recent_pace": 90.0, "gap_ahead": 0.0, "gap_behind": 0.0,
            "cumulative_time": 900.0, "pit_stops_taken": 0,
            "track_temp": 30.0, "air_temp": 25.0, "rainfall": 0.0, "track_status": "1"
        }
        strat_req = {
            "name": "S->M",
            "starting_compound": "SOFT",
            "planned_compounds": ["SOFT", "MEDIUM"],
            "pit_laps": [25]
        }
        res_sim = requests.post(f"{base_url}/strategy/simulate", json={"race_state": state_req, "strategy": strat_req})
        assert res_sim.status_code == 200
        print("[PASS] Phase 6 Simulation through API")
        
        # 8. Phase 7 Monte Carlo
        res_mc = requests.post(f"{base_url}/strategy/monte-carlo", json={"race_state": state_req, "strategy": strat_req, "simulation_count": 100})
        assert res_mc.status_code == 200
        print("[PASS] Phase 7 Monte Carlo through API")
        
        # 9. Phase 8 Optimizer
        res_opt = requests.post(f"{base_url}/strategy/optimize", json={"race_state": state_req, "candidate_strategies": [strat_req], "simulation_count": 100})
        assert res_opt.status_code == 200
        print("[PASS] Phase 8 Optimizer through API")
        
        # 10. Phase 9 Pit-Wall (Decision)
        res_pw = requests.post(f"{base_url}/pitwall/decision", json={"race_state": state_req, "simulation_count": 100})
        assert res_pw.status_code == 200
        print("[PASS] Phase 9 Pit-Wall through API")
        
        print("\nAll E2E Core API Tests Passed Successfully.")
        
    finally:
        server.terminate()
        server.wait()

if __name__ == "__main__":
    run_e2e_tests()
