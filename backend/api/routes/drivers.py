from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import text
from backend.api.dependencies import get_db
import os
import pandas as pd

router = APIRouter()

def _find_data_file(filename: str) -> str:
    candidates = [
        os.path.join("data", "Historical data", filename),
        os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", "data", "Historical data", filename)),
        os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "data", "Historical data", filename)),
        os.path.join("..", "data", "Historical data", filename),
    ]
    for c in candidates:
        if os.path.exists(c):
            return c
    return candidates[0]

def _get_csv_drivers():
    try:
        drivers_file = _find_data_file("drivers.csv")
        results_file = _find_data_file("results.csv")
        constructors_file = _find_data_file("constructors.csv")
        races_file = _find_data_file("races.csv")
        
        if not os.path.exists(drivers_file):
            return []
            
        df_d = pd.read_csv(drivers_file)
        
        # If results and races exist, find drivers from the latest season
        if os.path.exists(results_file) and os.path.exists(races_file) and os.path.exists(constructors_file):
            df_r = pd.read_csv(races_file)
            max_season = df_r['year'].max()
            recent_race_ids = df_r[df_r['year'] == max_season]['raceId'].unique()
            
            df_res = pd.read_csv(results_file)
            recent_res = df_res[df_res['raceId'].isin(recent_race_ids)]
            
            if not recent_res.empty:
                df_c = pd.read_csv(constructors_file)
                merged = recent_res.merge(df_d, on='driverId', how='inner')
                merged = merged.merge(df_c, on='constructorId', how='left')
                
                merged['pos_num'] = pd.to_numeric(merged['position'], errors='coerce').fillna(10.0)
                
                grouped = merged.groupby('driverId').agg({
                    'code': 'first',
                    'forename': 'first',
                    'surname': 'first',
                    'name': 'last',
                    'pos_num': 'mean'
                }).reset_index()
                
                drivers = []
                for _, row in grouped.iterrows():
                    avg_p = round(float(row['pos_num']), 1)
                    code_val = str(row['code']) if pd.notnull(row['code']) and str(row['code']) != '\\N' else str(row['surname'])[:3].upper()
                    c_name = str(row['name']) if pd.notnull(row['name']) else "Formula 1 Team"
                    drivers.append({
                        "driver_id": int(row['driverId']),
                        "ref": code_val,
                        "name": f"{row['forename']} {row['surname']}",
                        "constructor": c_name,
                        "avg_pos": avg_p,
                        "base_pace": round(88.0 + avg_p * 0.35, 2)
                    })
                drivers.sort(key=lambda x: x["name"])
                return drivers

        # Basic fallback from drivers.csv
        drivers = []
        for _, row in df_d.head(30).iterrows():
            code_val = str(row['code']) if pd.notnull(row['code']) and str(row['code']) != '\\N' else str(row['surname'])[:3].upper()
            drivers.append({
                "driver_id": int(row['driverId']),
                "ref": code_val,
                "name": f"{row['forename']} {row['surname']}",
                "constructor": "Formula 1 Team",
                "avg_pos": 10.0,
                "base_pace": 91.5
            })
        return drivers
    except Exception as e:
        print(f"Fallback CSV drivers error: {e}")
        return []

def _get_csv_driver_performance(driver_id: int, season: int = None, race_id: int = None):
    try:
        results_file = _find_data_file("results.csv")
        races_file = _find_data_file("races.csv")
        if not (os.path.exists(results_file) and os.path.exists(races_file)):
            return []
            
        df_res = pd.read_csv(results_file)
        df_r = pd.read_csv(races_file)
        
        user_res = df_res[df_res['driverId'] == driver_id]
        if user_res.empty:
            return []
            
        merged = user_res.merge(df_r, on='raceId', how='inner')
        if race_id:
            merged = merged[merged['raceId'] == race_id]
        elif season:
            merged = merged[merged['year'] == season]
            
        if merged.empty and season:
            merged = user_res.merge(df_r, on='raceId', how='inner')
            
        merged = merged.sort_values(by=['year', 'round'], ascending=[True, True]).tail(20)
        
        perf = []
        for _, r in merged.iterrows():
            pos = int(r['position']) if pd.notnull(r['position']) and str(r['position']).isdigit() else None
            perf.append({
                "driver_id": int(r['driverId']),
                "position": pos,
                "points": float(r['points']) if pd.notnull(r['points']) else 0.0,
                "laps": int(r['laps']) if pd.notnull(r['laps']) else 0,
                "fastest_lap": str(r['fastestLapTime']) if pd.notnull(r['fastestLapTime']) and str(r['fastestLapTime']) != '\\N' else None,
                "race_name": str(r['name']) if pd.notnull(r['name']) else "Grand Prix",
                "round": int(r['round']) if pd.notnull(r['round']) else 1
            })
        return perf
    except Exception as e:
        print(f"Fallback CSV performance error: {e}")
        return []

@router.get("")
def get_drivers(db: Session = Depends(get_db)):
    try:
        query = """
            SELECT 
                d.driver_id, 
                d.driver_code, 
                d.first_name, 
                d.last_name,
                COALESCE(MAX(c.constructor_name), 'Formula 1 Team') as team,
                COALESCE(ROUND(AVG(r.finish_position)::numeric, 1), 10.0) as avg_pos
            FROM drivers d 
            JOIN results r ON d.driver_id = r.driver_id 
            JOIN races rc ON r.race_id = rc.race_id 
            LEFT JOIN constructors c ON r.constructor_id = c.constructor_id
            WHERE rc.season = (SELECT MAX(season) FROM races)
            GROUP BY d.driver_id, d.driver_code, d.first_name, d.last_name
            ORDER BY d.last_name
        """
        try:
            result = db.execute(text(query)).fetchall()
        except Exception:
            return {"success": True, "data": _get_csv_drivers()}

        # Fallback: if latest-season join finds nothing, return all drivers
        if not result:
            try:
                fallback = "SELECT driver_id, driver_code, first_name, last_name, 'Formula 1 Team', 10.0 FROM drivers ORDER BY last_name LIMIT 100"
                result = db.execute(text(fallback)).fetchall()
            except Exception:
                return {"success": True, "data": _get_csv_drivers()}

        if not result:
            return {"success": True, "data": _get_csv_drivers()}

        drivers = [
            {
                "driver_id": r[0],
                "ref": r[1] or "",
                "name": f"{r[2]} {r[3]}",
                "constructor": r[4] or "Formula 1 Team",
                "avg_pos": float(r[5]) if r[5] else 10.0,
                # Fast front-runners have ~88.5s baseline pace, midfield ~91s, backmarkers ~93.5s
                "base_pace": round(88.0 + (float(r[5]) if r[5] else 10.0) * 0.35, 2)
            }
            for r in result
        ]
        return {"success": True, "data": drivers}
    except Exception as e:
        return {"success": True, "data": _get_csv_drivers()}

@router.get("/{driver_id}/performance")
def get_driver_performance(driver_id: int, season: int = None, race_id: int = None, db: Session = Depends(get_db)):
    try:
        query = """
            SELECT r.driver_id, r.finish_position, r.points, r.laps_completed, r.fastest_lap, rc.race_name, rc.round
            FROM results r
            JOIN races rc ON r.race_id = rc.race_id
            WHERE r.driver_id = :driver_id
        """
        params = {"driver_id": driver_id}
        
        if race_id:
            query += " AND r.race_id = :race_id"
            params["race_id"] = race_id
        elif season:
            query += " AND rc.season = :season"
            params["season"] = season
            
        query += " ORDER BY r.race_id DESC LIMIT 20"
            
        try:
            result = db.execute(text(query), params).fetchall()
        except Exception:
            return {"success": True, "data": _get_csv_driver_performance(driver_id, season, race_id)}
        
        if not result and season:
            try:
                # Fallback to recent races regardless of season
                fallback_query = """
                    SELECT r.driver_id, r.finish_position, r.points, r.laps_completed, r.fastest_lap, rc.race_name, rc.round
                    FROM results r
                    JOIN races rc ON r.race_id = rc.race_id
                    WHERE r.driver_id = :driver_id
                    ORDER BY r.race_id DESC LIMIT 20
                """
                result = db.execute(text(fallback_query), {"driver_id": driver_id}).fetchall()
            except Exception:
                return {"success": True, "data": _get_csv_driver_performance(driver_id, season, race_id)}
            
        if not result:
            return {"success": True, "data": _get_csv_driver_performance(driver_id, season, race_id)}
            
        # Chronological order
        ordered = list(reversed(result))
        perf = []
        for r in ordered:
            perf.append({
                "driver_id": r[0],
                "position": r[1],
                "points": r[2],
                "laps": r[3],
                "fastest_lap": str(r[4]) if r[4] is not None else None,
                "race_name": r[5] or "Grand Prix",
                "round": r[6]
            })
            
        return {"success": True, "data": perf}
    except Exception as e:
        return {"success": True, "data": _get_csv_driver_performance(driver_id, season, race_id)}
