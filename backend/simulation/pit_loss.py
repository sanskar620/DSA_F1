def get_pit_loss(circuit: str) -> float:
    """
    Estimates the pit-lane time loss based on historical data.
    If circuit data is unavailable, falls back to an average assumption.
    """
    # Hardcoded historical approximations for Phase 6 deterministic sim
    # In a full production system, this would query the PostgreSQL database.
    circuit_pit_loss = {
        "silverstone": 21.5,
        "monza": 23.0,
        "spa": 20.0,
        "monaco": 24.5,
        "bahrain": 22.8,
        "catalunya": 22.5
    }
    
    # Fallback to an F1 global average of ~22 seconds if circuit is missing
    return circuit_pit_loss.get(circuit.lower(), 22.0)
