from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import text
from backend.api.dependencies import get_db
from backend.api.schemas.race import RaceListResponse, RaceResponse
import os
import pandas as pd
from datetime import date as dt_date

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

def _get_csv_races(season: int = None):
    try:
        races_file = _find_data_file("races.csv")
        circuits_file = _find_data_file("circuits.csv")
        if not os.path.exists(races_file):
            return []
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
            res.append(RaceResponse(
                race_id=int(row['raceId']),
                season=int(row['year']),
                round=int(row['round']),
                name=str(row['name_x'] if 'name_x' in row else row['name']),
                circuit=str(row['name_y'] if 'name_y' in row and pd.notnull(row['name_y']) else 'Grand Prix Circuit'),
                date=d_val,
                total_laps=57
            ))
        return res
    except Exception as e:
        print(f"Fallback CSV races error: {e}")
        return []

def _get_csv_race_details(race_id: int):
    try:
        races_file = _find_data_file("races.csv")
        if not os.path.exists(races_file):
            return None
        df_r = pd.read_csv(races_file)
        match = df_r[df_r['raceId'] == race_id]
        if match.empty:
            return None
        row = match.iloc[0]
        return {
            "race_id": int(row['raceId']),
            "season": int(row['year']),
            "round": int(row['round']),
            "name": str(row['name']),
            "date": str(row['date'])
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
            races.append(RaceResponse(
                race_id=r[0],
                season=r[1],
                round=r[2],
                name=r[3],
                circuit=str(r[4]),
                date=r[5],
                total_laps=int(r[6]) if r[6] else 57
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
