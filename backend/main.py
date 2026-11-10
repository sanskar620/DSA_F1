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
    # Load ML models exactly once on startup
    model_loader.load_models()

@app.get("/")
def root():
    return {"message": "Welcome to F1 StrategyIQ API"}
