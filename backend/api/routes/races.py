from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import text
from backend.api.dependencies import get_db
from backend.api.schemas.race import RaceListResponse, RaceResponse

router = APIRouter()

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
            
        result = db.execute(text(query), params).fetchall()
        
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
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{race_id}")
def get_race_details(race_id: int, db: Session = Depends(get_db)):
    try:
        query = 'SELECT race_id, season, round, race_name, race_date FROM races WHERE race_id = :race_id'
        result = db.execute(text(query), {"race_id": race_id}).fetchone()
        
        if not result:
            raise HTTPException(status_code=404, detail="Race not found")
            
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
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
