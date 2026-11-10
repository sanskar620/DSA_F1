export type Compound = "SOFT" | "MEDIUM" | "HARD";

export type LapData = {
  lap: number;
  actual: number;
  predicted: number;
  position: number;
  gapAhead: number;
  gapBehind: number;
  tyreAge: number;
  compound: Compound;
  degradation: number;
  s1: number;
  s2: number;
  s3: number;
  safetyCar: boolean;
};

const driverOffsets: Record<string, number> = {
  "Charles Leclerc": 0.12,
  "Max Verstappen": -0.18,
  "Lando Norris": 0,
  "Oscar Piastri": 0.08,
  "Lewis Hamilton": 0.06,
};

export function getRaceData(driver = "Charles Leclerc", race = "Bahrain") {
  const offset = driverOffsets[driver] ?? 0;
  const raceOffset = race.length % 4;
  const positions = [8, 8, 7, 7, 7, 6, 6, 6, 6, 5, 5, 5, 5, 5, 4, 4, 4, 4, 4, 7, 7, 6, 6, 6, 5, 5, 5, 5, 5, 4, 4, 4, 4, 4, 3, 3, 3, 3, 6, 6, 5, 5, 5, 5, 4, 4, 4, 4, 4, 4, 3, 3, 3, 3, 3, 3, 3];

  return Array.from({ length: 57 }, (_, index): LapData => {
    const lap = index + 1;
    const stintStart = lap <= 20 ? 1 : lap <= 38 ? 21 : 39;
    const tyreAge = lap - stintStart + 1;
    const compound: Compound = lap <= 20 ? "MEDIUM" : lap <= 38 ? "HARD" : "MEDIUM";
    const fuelEffect = (57 - lap) * 0.052;
    const compoundDelta = compound === "HARD" ? 0.55 : 0.16;
    const degradation = tyreAge * (compound === "HARD" ? 0.055 : 0.082);
    const wave = Math.sin(lap * 1.71 + raceOffset) * 0.22 + Math.cos(lap * 0.43) * 0.1;
    const safetyCar = lap >= 27 && lap <= 29;
    const predicted = 91.7 + fuelEffect + compoundDelta + degradation + offset;
    const actual = predicted + wave + (safetyCar ? 4.8 : 0);
    return {
      lap,
      actual: Number(actual.toFixed(3)),
      predicted: Number(predicted.toFixed(3)),
      position: Math.max(1, (positions[index] ?? 5) + (driver === "Max Verstappen" ? -2 : driver === "Oscar Piastri" ? 1 : 0)),
      gapAhead: Number(Math.max(0.4, 3.5 - lap * 0.05 + Math.sin(lap * 0.7) * 0.5).toFixed(2)),
      gapBehind: Number(Math.max(0.5, 0.8 + lap * 0.025 + Math.cos(lap * 0.55) * 0.32).toFixed(2)),
      tyreAge,
      compound,
      degradation: Number((degradation / Math.max(tyreAge, 1)).toFixed(3)),
      s1: Number((29.8 + wave * 0.3 + offset).toFixed(2)),
      s2: Number((38.9 + wave * 0.45 + offset).toFixed(2)),
      s3: Number((23.6 + wave * 0.25 + offset).toFixed(2)),
      safetyCar,
    };
  });
}

export function getDriverData(driver: string) {
  const laps = getRaceData(driver);
  return {
    average: laps.reduce((sum, lap) => sum + lap.actual, 0) / laps.length,
    best: Math.min(...laps.map((lap) => lap.actual)),
    position: laps.reduce((sum, lap) => sum + lap.position, 0) / laps.length,
    stints: 3,
  };
}

export function predictLapTime(lap: LapData) { return lap.predicted; }
export function predictTyreDegradation(compound: Compound) { return compound === "SOFT" ? 0.13 : compound === "MEDIUM" ? 0.09 : 0.055; }

export const strategies = [
  { name: "M → H", full: "Medium → Hard", time: 5538, finish: "P4", podium: 42, win: 18, risk: "Low", pits: [22], tyres: ["M", "H"] },
  { name: "M → M → H", full: "Medium → Medium → Hard", time: 5525, finish: "P3", podium: 51, win: 24, risk: "Medium", pits: [19, 39], tyres: ["M", "M", "H"], recommended: true },
  { name: "S → M → H", full: "Soft → Medium → Hard", time: 5551, finish: "P5", podium: 35, win: 12, risk: "High", pits: [16, 37], tyres: ["S", "M", "H"] },
  { name: "M → H → S", full: "Medium → Hard → Soft", time: 5543, finish: "P4", podium: 39, win: 16, risk: "Medium", pits: [21, 48], tyres: ["M", "H", "S"] },
];

export function optimizeStrategy(risk = "Balanced") {
  if (risk === "Conservative") return strategies[0];
  if (risk === "Aggressive") return strategies[3];
  return strategies[1];
}

export function getPitwallDecision(lap: number, risk = "Balanced") {
  const urgency = risk === "Aggressive" ? 2 : risk === "Conservative" ? -2 : 0;
  if (lap >= 27 - urgency && lap <= 31) return { action: "PIT NOW", confidence: Math.min(94, 80 + lap - 24), tyre: "MEDIUM", tone: "critical" };
  if (lap >= 24 - urgency) return { action: "PIT WINDOW", confidence: 73, tyre: "MEDIUM", tone: "warning" };
  return { action: "STAY OUT", confidence: 77, tyre: "HARD", tone: "stable" };
}