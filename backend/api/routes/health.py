from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text
from backend.api.dependencies import get_db, get_predictor

router = APIRouter()

@router.get("/health")
def health_check(db: Session = Depends(get_db)):
    status = {
        "status": "ok",
        "database": "disconnected",
        "models": "unloaded"
    }
    
    # Check Database
    try:
        db.execute(text("SELECT 1"))
        status["database"] = "connected"
    except Exception as e:
        status["database"] = f"error: {str(e)}"
        
    # Check Models
    try:
        predictor = get_predictor()
        if predictor is not None:
            status["models"] = "loaded"
    except Exception as e:
        status["models"] = f"error: {str(e)}"
        
    return status
