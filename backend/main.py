from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import warnings
warnings.filterwarnings("ignore", category=UserWarning)

from backend.core.model_loader import model_loader

app = FastAPI(
    title="F1 StrategyIQ API",
    description="Data-Driven Race Strategy Optimization & Dynamic Pit-Wall Decision Support System",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # Allow all for local dev
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

from backend.api.routes import health, races, drivers, predictions, strategy, pitwall

app.include_router(health.router, prefix="/api", tags=["System"])
app.include_router(races.router, prefix="/api/races", tags=["Data"])
app.include_router(drivers.router, prefix="/api/drivers", tags=["Data"])
app.include_router(predictions.router, prefix="/api", tags=["ML Predictions"])
app.include_router(strategy.router, prefix="/api/strategy", tags=["Strategy"])
app.include_router(pitwall.router, prefix="/api/pitwall", tags=["Pit-Wall"])

@app.on_event("startup")
def startup_event():
    # 1. Load ML models exactly once on startup
    model_loader.load_models()

    # 2. Check and auto-initialize database if running for the first time
    try:
        from backend.api.dependencies import engine
        from sqlalchemy import text
        with engine.connect() as conn:
            table_check = conn.execute(
                text("SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'races');")
            ).scalar()
            if not table_check:
                print("Database tables not found. Automatically running initial schema & data loader...")
                from scripts.load_database import load_database
                load_database()
                print("Database auto-initialization complete.")
    except Exception as e:
        print(f"Database startup check note: {e}")

@app.get("/")
def root():
    return {"message": "Welcome to F1 StrategyIQ API"}
