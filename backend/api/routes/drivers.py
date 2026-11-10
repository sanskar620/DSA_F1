from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import text
from backend.api.dependencies import get_db

router = APIRouter()

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
        result = db.execute(text(query)).fetchall()

        # Fallback: if latest-season join finds nothing, return all drivers
        if not result:
            fallback = "SELECT driver_id, driver_code, first_name, last_name, 'Formula 1 Team', 10.0 FROM drivers ORDER BY last_name LIMIT 100"
            result = db.execute(text(fallback)).fetchall()

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
        raise HTTPException(status_code=500, detail=str(e))

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
            
        result = db.execute(text(query), params).fetchall()
        
        if not result and season:
            # Fallback to recent races regardless of season
            fallback_query = """
                SELECT r.driver_id, r.finish_position, r.points, r.laps_completed, r.fastest_lap, rc.race_name, rc.round
                FROM results r
                JOIN races rc ON r.race_id = rc.race_id
                WHERE r.driver_id = :driver_id
                ORDER BY r.race_id DESC LIMIT 20
            """
            result = db.execute(text(fallback_query), {"driver_id": driver_id}).fetchall()
            
        if not result:
            return {"success": True, "data": []}
            
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
        raise HTTPException(status_code=500, detail=str(e))
