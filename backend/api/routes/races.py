from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import text
from backend.api.dependencies import get_db
from backend.api.schemas.race import RaceListResponse, RaceResponse
import os
import pandas as pd
from datetime import date as dt_date

router = APIRouter()

CIRCUIT_DEFAULT_LAPS = {
    "monaco": 78,
    "monte carlo": 78,
    "spa": 44,
    "francorchamps": 44,
    "silverstone": 52,
    "monza": 53,
    "albert park": 58,
    "melbourne": 58,
    "suzuka": 53,
    "interlagos": 71,
    "sao paulo": 71,
    "brazil": 71,
    "hungaroring": 70,
    "red bull ring": 71,
    "spielberg": 71,
    "austria": 71,
    "zandvoort": 72,
    "dutch": 72,
    "las vegas": 50,
    "singapore": 62,
    "marina bay": 62,
    "jeddah": 50,
    "saudi": 50,
    "bahrain": 57,
    "sakhir": 57,
    "catalunya": 66,
    "barcelona": 66,
    "spanish": 66,
    "baku": 51,
    "azerbaijan": 51,
    "austin": 56,
    "americas": 56,
    "united states": 56,
    "miami": 57,
    "mexico": 71,
    "rodriguez": 71,
    "yas marina": 58,
    "abu dhabi": 58,
    "imola": 63,
    "emilia": 63,
    "shanghai": 56,
    "china": 56,
    "lusail": 57,
    "qatar": 57,
    "villeneuve": 70,
    "montreal": 70,
    "canada": 70,
}

def _resolve_total_laps(race_id: int, race_name: str, circuit_name: str = "", max_laps_map: dict = None) -> int:
    if max_laps_map and race_id in max_laps_map:
        val = max_laps_map[race_id]
        if isinstance(val, (int, float)) and 35 <= val <= 85:
            return int(val)
            
    combined = f"{race_name} {circuit_name}".lower()
    for key, laps in CIRCUIT_DEFAULT_LAPS.items():
        if key in combined:
            return laps
    return 57

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

def _get_csv_races(season: int = None):
    try:
        races_file = _find_data_file("races.csv")
        circuits_file = _find_data_file("circuits.csv")
        results_file = _find_data_file("results.csv")
        if not os.path.exists(races_file):
            return []
            
        max_laps_map = {}
        if os.path.exists(results_file):
            try:
                df_res = pd.read_csv(results_file, usecols=['raceId', 'laps'])
                max_laps_map = df_res.groupby('raceId')['laps'].max().to_dict()
            except Exception:
                pass

        df_r = pd.read_csv(races_file)
        df_c = pd.read_csv(circuits_file) if os.path.exists(circuits_file) else pd.DataFrame(columns=['circuitId', 'name'])
        df = df_r.merge(df_c, on='circuitId', how='left')
        if season:
            df = df[df['year'] == season]
        df = df.sort_values(by=['year', 'round'], ascending=[False, True]).head(100)
        res = []
        for _, row in df.iterrows():
            try:
                d_val = dt_date.fromisoformat(str(row['date']))
            except:
                d_val = dt_date(int(row['year']), 3, 1)
            r_id = int(row['raceId'])
            r_name = str(row['name_x'] if 'name_x' in row else row['name'])
            c_name = str(row['name_y'] if 'name_y' in row and pd.notnull(row['name_y']) else 'Grand Prix Circuit')
            laps_count = _resolve_total_laps(r_id, r_name, c_name, max_laps_map)
            res.append(RaceResponse(
                race_id=r_id,
                season=int(row['year']),
                round=int(row['round']),
                name=r_name,
                circuit=c_name,
                date=d_val,
                total_laps=laps_count
            ))
        return res
    except Exception as e:
        print(f"Fallback CSV races error: {e}")
        return []

def _get_csv_race_details(race_id: int):
    try:
        races_file = _find_data_file("races.csv")
        results_file = _find_data_file("results.csv")
        if not os.path.exists(races_file):
            return None
            
        max_laps_map = {}
        if os.path.exists(results_file):
            try:
                df_res = pd.read_csv(results_file, usecols=['raceId', 'laps'])
                max_laps_map = df_res.groupby('raceId')['laps'].max().to_dict()
            except Exception:
                pass

        df_r = pd.read_csv(races_file)
        match = df_r[df_r['raceId'] == race_id]
        if match.empty:
            return None
        row = match.iloc[0]
        r_name = str(row['name'])
        laps_count = _resolve_total_laps(race_id, r_name, "", max_laps_map)
        return {
            "race_id": int(row['raceId']),
            "season": int(row['year']),
            "round": int(row['round']),
            "name": r_name,
            "date": str(row['date']),
            "total_laps": laps_count
        }
    except Exception:
        return None

@router.get("", response_model=RaceListResponse)
def get_races(season: int = None, circuit: str = None, db: Session = Depends(get_db)):
    try:
        query = """
            SELECT 
                r.race_id, 
                r.season, 
                r.round, 
                r.race_name, 
                COALESCE(c.circuit_name, 'Grand Prix Circuit') as circuit, 
                r.race_date,
                COALESCE((SELECT MAX(res.laps_completed) FROM results res WHERE res.race_id = r.race_id), 57) as total_laps
            FROM races r 
            LEFT JOIN circuits c ON r.circuit_id = c.circuit_id 
            WHERE 1=1
        """
        params = {}
        
        if season:
            query += " AND r.season = :season"
            params["season"] = season
            
        query += " ORDER BY r.season DESC, r.round ASC LIMIT 100"
            
        try:
            result = db.execute(text(query), params).fetchall()
        except Exception:
            # Fallback to local historical CSVs if DB is provisioning/offline
            return RaceListResponse(success=True, data=_get_csv_races(season))
            
        if not result:
            return RaceListResponse(success=True, data=_get_csv_races(season))
        
        races = []
        for r in result:
            raw_laps = int(r[6]) if r[6] else None
            resolved_laps = raw_laps if raw_laps and 35 <= raw_laps <= 85 else _resolve_total_laps(r[0], r[3], str(r[4]))
            races.append(RaceResponse(
                race_id=r[0],
                season=r[1],
                round=r[2],
                name=r[3],
                circuit=str(r[4]),
                date=r[5],
                total_laps=resolved_laps
            ))
            
        return RaceListResponse(success=True, data=races)
    except Exception as e:
        return RaceListResponse(success=True, data=_get_csv_races(season))

@router.get("/{race_id}")
def get_race_details(race_id: int, db: Session = Depends(get_db)):
    try:
        query = 'SELECT race_id, season, round, race_name, race_date FROM races WHERE race_id = :race_id'
        try:
            result = db.execute(text(query), {"race_id": race_id}).fetchone()
        except Exception:
            result = None
        
        if result:
            return {
                "success": True,
                "data": {
                    "race_id": result[0],
                    "season": result[1],
                    "round": result[2],
                    "name": result[3],
                    "date": str(result[4])
                }
            }
            
        csv_detail = _get_csv_race_details(race_id)
        if csv_detail:
            return {"success": True, "data": csv_detail}
            
        raise HTTPException(status_code=404, detail="Race not found")
    except HTTPException:
        raise
    except Exception as e:
        csv_detail = _get_csv_race_details(race_id)
        if csv_detail:
            return {"success": True, "data": csv_detail}
        raise HTTPException(status_code=500, detail=str(e))
