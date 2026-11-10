const API_URL = import.meta.env.VITE_API_URL || "http://127.0.0.1:8000";

export async function fetchAPI(endpoint: string, options: RequestInit = {}) {
  const url = `${API_URL}${endpoint}`;
  try {
    const response = await fetch(url, {
      ...options,
      headers: {
        "Content-Type": "application/json",
        ...options.headers,
      },
    });

    if (!response.ok) {
      let message = `HTTP Error ${response.status}`;
      try {
        const errorData = await response.json();
        message = errorData.detail || message;
      } catch (e) {
        // Not JSON
      }
      throw new Error(message);
    }

    return await response.json();
  } catch (error) {
    console.error(`API Fetch Error [${endpoint}]:`, error);
    throw error;
  }
}

// ==========================================
// RACES & DRIVERS
// ==========================================
export async function getHealth() {
  return fetchAPI("/api/health");
}

export async function getRaces() {
  return fetchAPI("/api/races");
}

export async function getDrivers() {
  return fetchAPI("/api/drivers");
}

export async function getRaceDetails(raceId: number) {
  return fetchAPI(`/api/races/${raceId}`);
}

export async function getDriverPerformance(driverId: number, raceId?: number, season?: number) {
  const params = new URLSearchParams();
  if (raceId) params.append("race_id", raceId.toString());
  if (season) params.append("season", season.toString());
  const query = params.toString() ? `?${params.toString()}` : "";
  return fetchAPI(`/api/drivers/${driverId}/performance${query}`);
}

// ==========================================
// PREDICTIONS
// ==========================================
export interface RaceStatePayload {
  race_id: number;
  circuit?: string;
  driver_id?: number;
  driver?: string;
  constructor_id?: number;
  constructor?: string;
  current_lap: number;
  total_laps: number;
  laps_remaining: number;
  current_position: number;
  compound: string;
  tyre_age: number;
  stint: number;
  stint_lap: number;
  recent_pace: number;
  gap_ahead: number;
  gap_behind: number;
  cumulative_time: number;
  pit_stops_taken: number;
  track_temp: number;
  air_temp: number;
  rainfall: number;
  track_status: string;
  lap_number?: number;
}

export async function predictLapTime(payload: RaceStatePayload) {
  return fetchAPI("/api/predict/lap-time", {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export async function predictTyre(payload: RaceStatePayload) {
  return fetchAPI("/api/predict/tyre", {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export async function predictPitDecision(payload: RaceStatePayload) {
  return fetchAPI("/api/predict/pit-decision", {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

// ==========================================
// STRATEGY & MONTE CARLO
// ==========================================
export async function simulateStrategy(raceState: RaceStatePayload, strategy: any) {
  return fetchAPI("/api/strategy/simulate", {
    method: "POST",
    body: JSON.stringify({ race_state: raceState, strategy }),
  });
}

export async function runMonteCarlo(raceState: RaceStatePayload, strategy: any, count = 1000) {
  return fetchAPI("/api/strategy/monte-carlo", {
    method: "POST",
    body: JSON.stringify({ race_state: raceState, strategy, simulation_count: count }),
  });
}

export async function optimizeStrategy(raceState: RaceStatePayload, candidates: any[], count = 1000, objective = "BALANCED") {
  return fetchAPI("/api/strategy/optimize", {
    method: "POST",
    body: JSON.stringify({ race_state: raceState, candidate_strategies: candidates, simulation_count: count, objective }),
  });
}

// ==========================================
// DYNAMIC PIT-WALL
// ==========================================
export async function getPitWallDecision(raceState: RaceStatePayload, count = 1000) {
  return fetchAPI("/api/pitwall/decision", {
    method: "POST",
    body: JSON.stringify({ race_state: raceState, simulation_count: count }),
  });
}

export async function replayPitWall(raceId: number, driverId: number, startLap: number, endLap: number, count = 1000) {
  return fetchAPI("/api/pitwall/replay", {
    method: "POST",
    body: JSON.stringify({ race_id: raceId, driver_id: driverId, start_lap: startLap, end_lap: endLap, simulation_count: count }),
  });
}
