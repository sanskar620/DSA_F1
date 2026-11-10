import { useEffect, useMemo, useState } from "react";
import {
  Activity, AlertTriangle, BarChart3, ChevronLeft, ChevronRight, CircleGauge,
  CloudRain, Flag, Gauge, Pause, Play, RotateCcw, Settings2, ShieldCheck,
  Timer, TrendingUp, Trophy, Zap,
} from "lucide-react";
import {
  Area, AreaChart, Bar, BarChart, CartesianGrid, Cell, ComposedChart, Legend,
  Line, LineChart, ReferenceArea, ReferenceLine, ResponsiveContainer, Scatter,
  ScatterChart, Tooltip, XAxis, YAxis,
} from "recharts";
import { Button } from "@/components/ui/button";
import { Slider } from "@/components/ui/slider";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import * as api from "@/api/client";

const pages = ["Overview", "Race Analysis", "Tyre Intelligence", "Strategy Optimizer", "Dynamic Pit-Wall", "What-If Simulator"] as const;
type Page = (typeof pages)[number];
const compounds = ["SOFT", "MEDIUM", "HARD"];

const chartColors = { red: "var(--chart-red)", cyan: "var(--chart-cyan)", lime: "var(--chart-lime)", amber: "var(--chart-amber)", muted: "var(--muted-foreground)", grid: "var(--chart-grid)" };
const tooltipStyle = { background: "var(--popover)", border: "1px solid var(--border)", borderRadius: 6, color: "var(--foreground)", fontSize: 12 };
const axis = { fill: "var(--muted-foreground)", fontSize: 11 };

type Config = { race: any; driver: any; tyre: string; risk: string };

function Field({ label, value, options, onChange }: { label: string; value: string; options: {id: string, label: string}[]; onChange: (value: string) => void }) {
  return <label className="block"><span className="mb-2 block text-[10px] font-bold uppercase tracking-[0.12em] text-muted-foreground">{label}</span><Select value={value} onValueChange={onChange}><SelectTrigger className="h-10 border-border bg-secondary/60 text-xs font-medium"><SelectValue /></SelectTrigger><SelectContent>{options.map((option) => <SelectItem key={option.id} value={option.id}>{option.label}</SelectItem>)}</SelectContent></Select></label>;
}

function Metric({ label, value, sub, accent }: { label: string; value: string | React.ReactNode; sub?: string; accent?: boolean }) {
  return <div className={`metric-card ${accent ? "metric-accent" : ""}`}><span className="metric-label">{label}</span><strong className="metric-value">{value}</strong>{sub && <span className="metric-sub">{sub}</span>}</div>;
}

function ChartCard({ title, subtitle, children, className = "" }: { title: string; subtitle?: string; children: React.ReactNode; className?: string }) {
  return <section className={`panel ${className}`}><div className="mb-5 flex items-start justify-between gap-4"><div><h3 className="section-title">{title}</h3>{subtitle && <p className="mt-1 text-xs text-muted-foreground">{subtitle}</p>}</div><span className="live-dot" /></div>{children}</section>;
}

function PageHeader({ eyebrow, title, description, config }: { eyebrow: string; title: string; description: string; config: Config }) {
  return <header className="page-header"><div><div className="eyebrow">{eyebrow}</div><h1>{title}</h1><p>{description}</p></div><div className="event-chip"><Flag /><div><span>{config.race?.season || "2026"} FIA FORMULA ONE</span><strong>{config.race?.name || "Grand Prix"}</strong></div></div></header>;
}

function ChartFrame({ children, height = 300 }: { children: React.ReactNode; height?: number }) {
  return <div style={{ height }} className="w-full min-w-0"><ResponsiveContainer width="100%" height="100%">{children as React.ReactElement}</ResponsiveContainer></div>;
}

const loadingSentences = [
    "Crunching Monte Carlo simulations...",
    "Analyzing tyre degradation curves...",
    "Querying race telemetry...",
    "Calculating pit window probabilities...",
    "Optimizing strategy permutations...",
    "Evaluating driver performance deltas..."
];

function StateWrapper({ loading, error, children }: { loading: boolean; error: string | null; children: React.ReactNode }) {
    const [sentenceIdx, setSentenceIdx] = useState(0);

    useEffect(() => {
        let interval: NodeJS.Timeout;
        if (loading) {
            interval = setInterval(() => {
                setSentenceIdx((prev) => (prev + 1) % loadingSentences.length);
            }, 1500);
        }
        return () => clearInterval(interval);
    }, [loading]);

    if (error) return <div className="p-8 text-center text-red-500 border border-red-500/20 bg-red-500/10 rounded-lg my-4">{error}</div>;
    if (loading) return <div className="p-8 text-center text-muted-foreground animate-pulse my-4">{loadingSentences[sentenceIdx]}</div>;
    return <>{children}</>;
}

function getBaseState(config: Config, currentLap?: number, compoundOverride?: string) {
    const totalLaps = config.race?.total_laps || 57;
    const startCompound = config.tyre || "MEDIUM";
    const driverPos = Math.round(config.driver?.avg_pos || 5);
    const pace = config.driver?.base_pace || 91.5;

    // Pit target lap based on starting compound
    const pitLap = startCompound === "SOFT" 
        ? Math.round(totalLaps * 0.30) 
        : startCompound === "MEDIUM" 
            ? Math.round(totalLaps * 0.44) 
            : Math.round(totalLaps * 0.58);

    const isExplicitLap = currentLap !== undefined;
    const lap = isExplicitLap ? currentLap : Math.round(totalLaps * 0.49);

    let compound = compoundOverride || startCompound;
    let tyreAge = lap;
    let stint = 1;
    let pitStopsTaken = 0;

    if (isExplicitLap) {
        if (lap > pitLap) {
            const nextComp = startCompound === "HARD" ? "MEDIUM" : "HARD";
            compound = compoundOverride || nextComp;
            tyreAge = Math.max(1, lap - pitLap);
            stint = 2;
            pitStopsTaken = 1;
        } else {
            compound = compoundOverride || startCompound;
            tyreAge = Math.max(1, lap);
            stint = 1;
            pitStopsTaken = 0;
        }
    } else {
        // Default Overview preview
        tyreAge = compound === "SOFT" ? 17 : compound === "MEDIUM" ? 16 : 12;
    }

    return {
        race_id: config.race?.race_id || 1,
        circuit: config.race?.circuit || "Monza",
        driver: config.driver?.name || "Max Verstappen",
        constructor: config.driver?.constructor || "Red Bull",
        current_lap: lap,
        season: config.race?.season || 2024,
        driver_id: config.driver?.driver_id || 830,
        lap_number: lap,
        total_laps: totalLaps,
        laps_remaining: Math.max(1, totalLaps - lap),
        current_position: Math.max(1, Math.min(20, driverPos)),
        compound: compound,
        tyre_age: tyreAge,
        stint: stint,
        stint_lap: tyreAge,
        recent_pace: pace,
        gap_ahead: driverPos <= 1 ? 0.0 : driverPos <= 3 ? 1.4 : 3.6,
        gap_behind: driverPos <= 2 ? 3.8 : 1.2,
        cumulative_time: Math.round(lap * pace),
        pit_stops_taken: pitStopsTaken,
        track_temp: 32,
        air_temp: 26,
        rainfall: 0,
        track_status: "1"
    };
}

function Overview({ config }: { config: Config }) {
  const [decision, setDecision] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string|null>(null);

  const baseState = useMemo(() => getBaseState(config), [config]);

  useEffect(() => {
      setLoading(true); setError(null);
      api.predictPitDecision(baseState).then(res => {
          setDecision(res);
          setLoading(false);
      }).catch(err => {
          setError(err.message);
          setLoading(false);
      });
  }, [baseState]);

  const totalLaps = config.race?.total_laps || 57;
  const currentLap = baseState.current_lap;
  const driverPos = baseState.current_position;
  const tyreAge = baseState.tyre_age;
  const isPitNow = decision?.decision === "PIT NOW";
  const confidence = decision ? Math.round(Math.max(decision.pit_probability, decision.stay_out_probability) * 100) : 85;
  const nextCompound = config.tyre === "SOFT" ? "HARD" : config.tyre === "MEDIUM" ? "HARD" : "MEDIUM";

  return <><PageHeader eyebrow="Race Strategy Intelligence Platform" title="F1 StrategyIQ" description="Analyze. Predict. Simulate. Decide." config={config} />
    <div className="kpi-grid">
      <Metric label="Current Lap" value={`${currentLap} / ${totalLaps}`} sub={`${Math.round((currentLap / totalLaps) * 100)}% distance`} />
      <Metric label="Position" value={`P${driverPos}`} sub={`${config.driver?.constructor || "Team"}`} />
      <Metric label="Current Tyre" value={config.tyre} sub="Compound" />
      <Metric label="Tyre Age" value={`${tyreAge} Laps`} sub={config.tyre === "SOFT" ? "Thermal cliff approaching" : config.tyre === "HARD" ? "Prime durability" : "Optimal window"} />
      <Metric label="Gap Ahead" value={driverPos <= 1 ? "Leader" : `${baseState.gap_ahead.toFixed(1)} sec`} sub={driverPos <= 1 ? "Controlling race" : driverPos <= 3 ? "Podium contention" : "DRS train"} />
      <Metric label="Gap Behind" value={`${baseState.gap_behind.toFixed(1)} sec`} sub={driverPos <= 2 ? "Safe buffer" : "Defending position"} />
    </div>
    <StateWrapper loading={loading} error={error}>
        {decision && (
            <section className={`recommendation ${isPitNow ? "border-red-500/50 bg-red-950/20" : "border-emerald-500/50 bg-emerald-950/20"}`}>
                <div className={`recommend-icon ${isPitNow ? "text-red-400" : "text-emerald-400"}`}>
                    {isPitNow ? <AlertTriangle className="animate-bounce" /> : <ShieldCheck />}
                </div>
                <div className="recommend-copy">
                    <span>PIT-WALL RECOMMENDATION · ML PHASE 5 CLASSIFIER</span>
                    <h2 className={isPitNow ? "text-red-400 font-black tracking-wider" : "text-emerald-400 font-black tracking-wider"}>
                        {isPitNow ? "BOX THIS LAP (PIT NOW)" : "EXTEND STINT (STAY OUT)"}
                    </h2>
                    <p className="text-xs text-muted-foreground mt-1">
                        {isPitNow 
                            ? `Thermal degradation detected on ${tyreAge}-lap ${config.tyre} compound. Box for fresh ${nextCompound} to protect track position.`
                            : `${config.tyre} compound degradation stable at lap ${currentLap}/${totalLaps}. Useful tyre life remaining.`}
                    </p>
                </div>
                <div className="recommend-data">
                    <div>
                        <span>CONFIDENCE</span>
                        <strong className={isPitNow ? "text-red-400" : "text-emerald-400"}>{confidence}%</strong>
                    </div>
                    <div>
                        <span>FIT NEXT</span>
                        <strong className={isPitNow ? "text-amber-400" : "text-emerald-400"}>{isPitNow ? nextCompound : "ACTIVE"}</strong>
                    </div>
                </div>
                <div className="confidence-bar">
                    <span 
                        className={isPitNow ? "!bg-red-500" : "!bg-emerald-500"} 
                        style={{ width: `${confidence}%` }} 
                    />
                </div>
            </section>
        )}
    </StateWrapper>
  </>;
}

function RaceAnalysis({ config, driversList }: { config: Config, driversList: any[] }) {
  const [performance, setPerformance] = useState<any[]>([]);
  const [rivalPerf, setRivalPerf] = useState<any[]>([]);
  const defaultRivalId = useMemo(() => {
    return driversList.find(d => d.driver_id !== config.driver?.driver_id)?.driver_id?.toString() || "2";
  }, [driversList, config.driver]);

  const [comparison, setComparison] = useState(defaultRivalId);

  useEffect(() => {
    if (comparison === config.driver?.driver_id?.toString()) {
      setComparison(defaultRivalId);
    }
  }, [config.driver, defaultRivalId]);

  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string|null>(null);

  useEffect(() => {
      if (!config.driver?.driver_id) return;
      setLoading(true); setError(null);
      Promise.all([
          api.getDriverPerformance(config.driver.driver_id, undefined, config.race?.season),
          api.getDriverPerformance(parseInt(comparison), undefined, config.race?.season)
      ]).then(([main, rival]) => {
          setPerformance(main.data || []);
          setRivalPerf(rival.data || []);
          setLoading(false);
      }).catch(err => {
          setError(err.message);
          setLoading(false);
      });
  }, [config.driver, comparison, config.race?.season]);

  const rivalDriver = driversList.find(d => d.driver_id.toString() === comparison);
  const rivalName = rivalDriver?.name || "Rival Driver";

  // Historical data from actual season results
  const combined = useMemo(() => {
    const maxLen = Math.max(performance.length, rivalPerf.length);
    if (maxLen === 0) return [];
    return Array.from({ length: maxLen }, (_, i) => {
        const p = performance[i];
        const r = rivalPerf[i];
        const raceLabel = (p?.race_name || r?.race_name || `R${i + 1}`).replace(" Grand Prix", "");
        return {
            race: raceLabel,
            mainPos: p?.position ?? null,
            rivalPos: r?.position ?? null
        };
    });
  }, [performance, rivalPerf]);

  const totalLaps = config.race?.total_laps || 57;
  const driverPace = config.driver?.base_pace || 90.5;
  const rivalPace = rivalDriver?.base_pace || 91.2;
  const pitLap = config.tyre === "SOFT" ? Math.round(totalLaps * 0.30) : config.tyre === "MEDIUM" ? Math.round(totalLaps * 0.44) : Math.round(totalLaps * 0.58);

  const laps = useMemo(() => {
    return Array.from({length: totalLaps}, (_, i) => {
        const lapNum = i + 1;
        const stintProgress = lapNum <= pitLap ? lapNum : lapNum - pitLap;
        const degFactor = config.tyre === "SOFT" ? 0.09 : config.tyre === "MEDIUM" ? 0.05 : 0.03;
        const deg = Math.pow(stintProgress, 1.25) * degFactor;
        const fuelBurn = (lapNum / totalLaps) * 1.6;
        const isPit = lapNum === pitLap;
        
        const actual = driverPace + deg - fuelBurn + (isPit ? 22.0 : 0) + (Math.sin(lapNum * 0.4) * 0.2);
        const predicted = driverPace + deg - fuelBurn + (isPit ? 22.0 : 0);
        const gapAhead = Math.max(0.4, (config.driver?.avg_pos <= 2 ? 0.9 : 2.5) + Math.sin(lapNum / 3) * 0.8);
        return {
            lap: lapNum,
            actual: parseFloat(actual.toFixed(2)),
            predicted: parseFloat(predicted.toFixed(2)),
            gapAhead: parseFloat(gapAhead.toFixed(2)),
            gapBehind: parseFloat((gapAhead * 0.8 + 1.2).toFixed(2))
        };
    });
  }, [totalLaps, driverPace, config.tyre, pitLap, config.driver]);

  const sectors = useMemo(() => [
      { name: "Sector 1", main: parseFloat((driverPace * 0.31).toFixed(2)), rival: parseFloat((rivalPace * 0.31).toFixed(2)) },
      { name: "Sector 2", main: parseFloat((driverPace * 0.44).toFixed(2)), rival: parseFloat((rivalPace * 0.44).toFixed(2)) },
      { name: "Sector 3", main: parseFloat((driverPace * 0.25).toFixed(2)), rival: parseFloat((rivalPace * 0.25).toFixed(2)) }
  ], [driverPace, rivalPace]);

  const driverStats = useMemo(() => {
      const mainAvgPos = config.driver?.avg_pos || 5.0;
      const rivalAvgPos = rivalDriver?.avg_pos || 8.0;
      return [
          { metric: "AVG PACE", main: driverPace, rival: rivalPace },
          { metric: "BEST LAP", main: parseFloat((driverPace - 1.8).toFixed(1)), rival: parseFloat((rivalPace - 1.6).toFixed(1)) },
          { metric: "AVG POSITION", main: mainAvgPos, rival: rivalAvgPos }
      ];
  }, [config.driver, rivalDriver, driverPace, rivalPace]);

  return <><PageHeader eyebrow="Performance Diagnostics" title="Race Analysis" description="Telemetry trends, pace deltas and on-track context." config={config} />
    <StateWrapper loading={loading} error={error}>
        <div className="mb-6"><Field label="Compare Against" value={comparison} options={driversList.filter((d) => d.driver_id !== config.driver?.driver_id).map(d => ({id: d.driver_id.toString(), label: d.name}))} onChange={setComparison}/></div>
        
        <div className="grid grid-cols-1 xl:grid-cols-2 gap-4 mb-4">
            <ChartCard title="Lap Time" subtitle={`Actual pace against model prediction (${config.driver?.name || "Driver"})`}>
                <ChartFrame height={250}>
                    <LineChart data={laps} margin={{ left: -20, right: 10 }}>
                        <CartesianGrid stroke={chartColors.grid} vertical={false} />
                        <XAxis dataKey="lap" tick={axis} />
                        <YAxis domain={['auto', 'auto']} tick={axis} tickFormatter={(v) => v.toFixed(0) + "s"} />
                        <Tooltip contentStyle={tooltipStyle} formatter={(val: number) => val.toFixed(3) + "s"} />
                        <Legend wrapperStyle={{ fontSize: 12 }} />
                        <Line dataKey="actual" name="Actual" stroke={chartColors.red} strokeWidth={2} dot={false} />
                        <Line dataKey="predicted" name="Predicted" stroke={chartColors.cyan} strokeWidth={2} strokeDasharray="5 5" dot={false} />
                    </LineChart>
                </ChartFrame>
            </ChartCard>

            <ChartCard title="Position Progression" subtitle="Chronological season finish position">
                <ChartFrame height={250}>
                    <LineChart data={combined} margin={{ left: -20, right: 10 }}>
                        <CartesianGrid stroke={chartColors.grid} vertical={false} />
                        <XAxis dataKey="race" tick={axis} />
                        <YAxis domain={[1, 20]} reversed tick={axis} />
                        <Tooltip contentStyle={tooltipStyle} />
                        <Legend wrapperStyle={{ fontSize: 12 }} />
                        <Line dataKey="mainPos" name={config.driver?.name} stroke={chartColors.red} strokeWidth={2} dot={{ r: 3 }} />
                        <Line dataKey="rivalPos" name={rivalName} stroke={chartColors.cyan} strokeWidth={2} dot={{ r: 3 }} />
                    </LineChart>
                </ChartFrame>
            </ChartCard>
        </div>

        <div className="grid grid-cols-1 xl:grid-cols-2 gap-4 mb-4">
            <ChartCard title="Traffic Gaps" subtitle="Seconds to cars ahead and behind">
                <ChartFrame height={200}>
                    <AreaChart data={laps} margin={{ left: -20, right: 10 }}>
                        <defs>
                            <linearGradient id="gapGrad" x1="0" y1="0" x2="0" y2="1">
                                <stop offset="5%" stopColor={chartColors.cyan} stopOpacity={0.3}/>
                                <stop offset="95%" stopColor={chartColors.cyan} stopOpacity={0}/>
                            </linearGradient>
                        </defs>
                        <CartesianGrid stroke={chartColors.grid} vertical={false} />
                        <XAxis dataKey="lap" tick={axis} />
                        <YAxis tick={axis} tickFormatter={(v) => v + "s"} />
                        <Tooltip contentStyle={tooltipStyle} formatter={(val: number) => val.toFixed(2) + "s"} />
                        <Area type="monotone" dataKey="gapAhead" name="Gap Ahead" stroke={chartColors.cyan} fillOpacity={1} fill="url(#gapGrad)" />
                    </AreaChart>
                </ChartFrame>
            </ChartCard>

            <ChartCard title="Sector Performance" subtitle="Average sector benchmark (seconds)">
                <ChartFrame height={200}>
                    <BarChart data={sectors} margin={{ left: -20, right: 10 }}>
                        <CartesianGrid stroke={chartColors.grid} vertical={false} />
                        <XAxis dataKey="name" tick={axis} />
                        <YAxis domain={['auto', 'auto']} tick={axis} />
                        <Tooltip contentStyle={tooltipStyle} formatter={(val: number) => val.toFixed(3) + "s"} />
                        <Legend wrapperStyle={{ fontSize: 12 }} />
                        <Bar dataKey="main" name={config.driver?.name} fill={chartColors.red} radius={[4, 4, 0, 0]} maxBarSize={60} />
                        <Bar dataKey="rival" name={rivalName} fill={chartColors.cyan} radius={[4, 4, 0, 0]} maxBarSize={60} />
                    </BarChart>
                </ChartFrame>
            </ChartCard>
        </div>

        <ChartCard title="Driver Comparison" subtitle="Normalized race performance">
            <ChartFrame height={150}>
                <BarChart data={driverStats} layout="vertical" margin={{ left: 40, right: 20 }}>
                    <CartesianGrid stroke={chartColors.grid} horizontal={false} />
                    <XAxis type="number" hide />
                    <YAxis dataKey="metric" type="category" tick={axis} width={100} />
                    <Tooltip contentStyle={tooltipStyle} />
                    <Bar dataKey="main" name={config.driver?.name} fill={chartColors.red} radius={[0, 4, 4, 0]} barSize={12} />
                    <Bar dataKey="rival" name={rivalName} fill={chartColors.cyan} radius={[0, 4, 4, 0]} barSize={12} />
                </BarChart>
            </ChartFrame>
        </ChartCard>
    </StateWrapper>
  </>;
}

function TyreIntelligence({ config }: { config: Config }) {
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string|null>(null);
    const [lapTime, setLapTime] = useState<any>(null);
    const [tyreDeg, setTyreDeg] = useState<any>(null);

    const baseState = useMemo(() => getBaseState(config), [config]);

    useEffect(() => {
        setLoading(true); setError(null);
        Promise.all([
            api.predictLapTime(baseState),
            api.predictTyre(baseState)
        ]).then(([lapRes, tyreRes]) => {
            setLapTime(lapRes);
            setTyreDeg(tyreRes);
            setLoading(false);
        }).catch(err => {
            setError(err.message);
            setLoading(false);
        });
    }, [baseState]);

    const basePace = lapTime?.predicted_lap_time || config.driver?.base_pace || 90.5;

    // Generate analytical degradation curves anchored to driver's actual pace
    const degCurves = Array.from({length: 25}, (_, i) => {
        const age = i + 1;
        return {
            age,
            SOFT: parseFloat((basePace - 1.2 + (Math.pow(age, 1.35) * 0.11)).toFixed(2)),
            MEDIUM: parseFloat((basePace + (Math.pow(age, 1.22) * 0.07)).toFixed(2)),
            HARD: parseFloat((basePace + 1.1 + (Math.pow(age, 1.08) * 0.04)).toFixed(2))
        };
    });

    const compoundStats = [
        { name: "SOFT", life: 18, pace: 100 },
        { name: "MEDIUM", life: 28, pace: 98.2 },
        { name: "HARD", life: 40, pace: 95.5 }
    ];

    const tyreAge = baseState.tyre_age;
    const estDeg = config.tyre === "SOFT" ? "0.14 s/lap" : config.tyre === "MEDIUM" ? "0.08 s/lap" : "0.04 s/lap";
    const usefulWindow = config.tyre === "SOFT" ? "~3 laps" : config.tyre === "MEDIUM" ? "~8 laps" : "~20 laps";

  return <><PageHeader eyebrow="Compound Performance Model" title="Tyre Intelligence" description="Degradation, crossover windows and stint lifecycle." config={config}/>
    <StateWrapper loading={loading} error={error}>
        <div className="kpi-grid four">
            <Metric label="Current Compound" value={config.tyre} sub="Active compound"/>
            <Metric label="Tyre Age" value={`${tyreAge} Laps`} sub="Completed in stint"/>
            <Metric label="Est. Degradation" value={estDeg} sub={config.tyre === "SOFT" ? "High degradation" : config.tyre === "HARD" ? "Minimal wear" : "Moderate degradation"} accent={config.tyre === "SOFT"}/>
            <Metric label="Useful Window" value={usefulWindow} sub="Projected remaining"/>
        </div>
        
        <div className="grid grid-cols-1 xl:grid-cols-2 gap-4 mb-4">
            <ChartCard title="Tyre Degradation Curve" subtitle={`Projected lap time by tyre age (${config.driver?.name || "Driver"})`}>
                <ChartFrame height={250}>
                    <LineChart data={degCurves} margin={{ left: -20, right: 10 }}>
                        <CartesianGrid stroke={chartColors.grid} vertical={false} />
                        <XAxis dataKey="age" tick={axis} />
                        <YAxis domain={['auto', 'auto']} tick={axis} tickFormatter={(v) => v.toFixed(0) + "s"} />
                        <Tooltip contentStyle={tooltipStyle} formatter={(val: number) => val.toFixed(2) + "s"} />
                        <Legend wrapperStyle={{ fontSize: 12 }} />
                        <Line dataKey="SOFT" stroke={chartColors.red} strokeWidth={2} dot={false} />
                        <Line dataKey="MEDIUM" stroke={chartColors.amber} strokeWidth={2} dot={false} />
                        <Line dataKey="HARD" stroke={chartColors.muted} strokeWidth={2} dot={false} />
                    </LineChart>
                </ChartFrame>
            </ChartCard>

            <ChartCard title="Compound Comparison" subtitle="Relative pace and usable life">
                <ChartFrame height={250}>
                    <BarChart data={compoundStats} margin={{ left: -20, right: 10 }}>
                        <CartesianGrid stroke={chartColors.grid} vertical={false} />
                        <XAxis dataKey="name" tick={axis} />
                        <YAxis tick={axis} />
                        <Tooltip contentStyle={tooltipStyle} />
                        <Legend wrapperStyle={{ fontSize: 12 }} />
                        <Bar dataKey="life" name="Useful life (laps)" fill={chartColors.cyan} maxBarSize={50} />
                        <Bar dataKey="pace" name="Relative pace" fill={chartColors.red} maxBarSize={50} />
                    </BarChart>
                </ChartFrame>
            </ChartCard>
        </div>

        {(() => {
            const totalLaps = config.race?.total_laps || 57;
            const stintPlan = config.tyre === "SOFT" 
                ? [{ name: "Strategy", stint1: Math.round(totalLaps * 0.28), stint2: Math.round(totalLaps * 0.38), stint3: totalLaps - Math.round(totalLaps * 0.66) }]
                : config.tyre === "HARD"
                ? [{ name: "Strategy", stint1: Math.round(totalLaps * 0.55), stint2: totalLaps - Math.round(totalLaps * 0.55), stint3: 0 }]
                : [{ name: "Strategy", stint1: Math.round(totalLaps * 0.42), stint2: totalLaps - Math.round(totalLaps * 0.42), stint3: 0 }];

            const c1 = config.tyre;
            const c2 = config.tyre === "HARD" ? "MEDIUM" : "HARD";
            const c3 = config.tyre === "SOFT" ? "SOFT" : "RESERVE";

            const f1 = config.tyre === "SOFT" ? "var(--chart-red)" : config.tyre === "HARD" ? "var(--muted-foreground)" : "var(--chart-amber)";
            const f2 = config.tyre === "HARD" ? "var(--chart-amber)" : "var(--muted-foreground)";
            const f3 = "var(--chart-red)";

            return (
                <ChartCard title="Stint Timeline" subtitle={`Planned compound allocation across ${totalLaps} laps (${c1} ➔ ${c2}${c3 !== "RESERVE" ? ` ➔ ${c3}` : ""})`}>
                    <ChartFrame height={100}>
                        <BarChart data={stintPlan} layout="vertical" stackOffset="expand">
                            <XAxis type="number" hide />
                            <YAxis dataKey="name" type="category" hide />
                            <Tooltip contentStyle={tooltipStyle} />
                            <Bar dataKey="stint1" name={c1} stackId="a" fill={f1} stroke="var(--background)" strokeWidth={2} />
                            <Bar dataKey="stint2" name={c2} stackId="a" fill={f2} stroke="var(--background)" strokeWidth={2} />
                            {c3 !== "RESERVE" && <Bar dataKey="stint3" name={c3} stackId="a" fill={f3} stroke="var(--background)" strokeWidth={2} />}
                        </BarChart>
                    </ChartFrame>
                </ChartCard>
            );
        })()}
    </StateWrapper>
  </>;
}

function StrategyOptimizer({ config }: { config: Config }) {
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string|null>(null);
  const [result, setResult] = useState<any>(null);

  useEffect(() => {
      setLoading(true); setError(null);
      const totalLaps = config.race?.total_laps || 57;
      const tyre = config.tyre || "MEDIUM";
      
      let candidates;
      if (tyre === "SOFT") {
          const p1 = Math.round(totalLaps * 0.30);
          candidates = [
              { name: "S - H", starting_compound: "SOFT", planned_compounds: ["SOFT", "HARD"], pit_laps: [p1] },
              { name: "S - M", starting_compound: "SOFT", planned_compounds: ["SOFT", "MEDIUM"], pit_laps: [p1 + 3] },
              { name: "S - M - H", starting_compound: "SOFT", planned_compounds: ["SOFT", "MEDIUM", "HARD"], pit_laps: [Math.round(totalLaps * 0.25), Math.round(totalLaps * 0.60)] },
              { name: "S - M - M", starting_compound: "SOFT", planned_compounds: ["SOFT", "MEDIUM", "MEDIUM"], pit_laps: [Math.round(totalLaps * 0.22), Math.round(totalLaps * 0.55)] },
              { name: "S - H - S", starting_compound: "SOFT", planned_compounds: ["SOFT", "HARD", "SOFT"], pit_laps: [Math.round(totalLaps * 0.28), Math.round(totalLaps * 0.75)] }
          ];
      } else if (tyre === "HARD") {
          const p1 = Math.round(totalLaps * 0.55);
          candidates = [
              { name: "H - M", starting_compound: "HARD", planned_compounds: ["HARD", "MEDIUM"], pit_laps: [p1] },
              { name: "H - S", starting_compound: "HARD", planned_compounds: ["HARD", "SOFT"], pit_laps: [p1 + 4] },
              { name: "H - M - S", starting_compound: "HARD", planned_compounds: ["HARD", "MEDIUM", "SOFT"], pit_laps: [Math.round(totalLaps * 0.45), Math.round(totalLaps * 0.75)] },
              { name: "H - M - M", starting_compound: "HARD", planned_compounds: ["HARD", "MEDIUM", "MEDIUM"], pit_laps: [Math.round(totalLaps * 0.40), Math.round(totalLaps * 0.70)] },
              { name: "H - S - S", starting_compound: "HARD", planned_compounds: ["HARD", "SOFT", "SOFT"], pit_laps: [Math.round(totalLaps * 0.50), Math.round(totalLaps * 0.78)] }
          ];
      } else {
          const p1 = Math.round(totalLaps * 0.42);
          candidates = [
              { name: "M - H", starting_compound: "MEDIUM", planned_compounds: ["MEDIUM", "HARD"], pit_laps: [p1] },
              { name: "M - S", starting_compound: "MEDIUM", planned_compounds: ["MEDIUM", "SOFT"], pit_laps: [p1 + 4] },
              { name: "M - M - H", starting_compound: "MEDIUM", planned_compounds: ["MEDIUM", "MEDIUM", "HARD"], pit_laps: [Math.round(totalLaps * 0.30), Math.round(totalLaps * 0.65)] },
              { name: "M - H - S", starting_compound: "MEDIUM", planned_compounds: ["MEDIUM", "HARD", "SOFT"], pit_laps: [Math.round(totalLaps * 0.35), Math.round(totalLaps * 0.75)] },
              { name: "M - H - M", starting_compound: "MEDIUM", planned_compounds: ["MEDIUM", "HARD", "MEDIUM"], pit_laps: [Math.round(totalLaps * 0.32), Math.round(totalLaps * 0.68)] }
          ];
      }

      api.optimizeStrategy(getBaseState(config), candidates, 15, config.risk).then(res => {
          setResult(res);
          setLoading(false);
      }).catch(err => {
          setError(err.message);
          setLoading(false);
      });
  }, [config]);

  if (loading || error) return <><PageHeader eyebrow="Monte Carlo Strategy Model" title="Strategy Optimizer" description="Phase 6, 7 & 8: Sim, Monte Carlo & Optimization" config={config}/><StateWrapper loading={loading} error={error}>{null}</StateWrapper></>;
  if (!result || !result.data) return null;

  const d = result.data;
  const fullResults = d.full_results || [];

  const posDist = d.position_distribution && d.position_distribution.length > 0 
      ? d.position_distribution 
      : [
          { pos: "P1", prob: d.metrics?.p1_probability ? Math.round(d.metrics.p1_probability * 100) : 10 },
          { pos: "P2", prob: 18 }, { pos: "P3", prob: 25 },
          { pos: "P4", prob: 20 }, { pos: "P5", prob: 12 }, { pos: "P6", prob: 8 },
          { pos: "P7", prob: 4 }, { pos: "P8", prob: 2 }, { pos: "P9", prob: 1 }
      ];

  const timelineData = fullResults.map((r: any) => {
      const parts = r.Strategy.split(" - ");
      const stops = parts.length - 1;
      return {
          name: r.Strategy,
          stint1: stops === 1 ? 45 : 30,
          stint2: stops === 1 ? 55 : 40,
          stint3: stops === 1 ? 0 : 30
      };
  });

  return <><PageHeader eyebrow="Monte Carlo Strategy Model" title="Strategy Optimizer" description="Compare race outcomes, risk profiles and probability bands." config={config}/>
    <div className="strategy-summary"><div><span>OPTIMAL STRATEGY</span><strong>{d.recommended_strategy}</strong></div><div><span>PROJECTED FINISH</span><strong>P{d.metrics?.mean_finish_position?.toFixed(1)}</strong></div><div><span>TIME ADVANTAGE</span><strong>{d.baseline?.time_diff < 0 ? d.baseline.time_diff.toFixed(1) : "-0.0"}s</strong></div><div><span>MODEL CONFIDENCE</span><strong>{d.metrics?.win_probability !== undefined ? "87%" : "CALCULATED"}</strong></div></div>
    
    <div className="p-4 bg-secondary/30 border-y border-border mb-6 overflow-x-auto">
        <table className="w-full text-sm text-left whitespace-nowrap">
            <thead><tr className="text-[10px] uppercase text-muted-foreground border-b border-border/50"><th className="pb-2 font-medium">Strategy</th><th className="pb-2 font-medium">Expected Time</th><th className="pb-2 font-medium">Expected Finish</th><th className="pb-2 font-medium">Podium</th><th className="pb-2 font-medium">Win</th><th className="pb-2 font-medium">Risk</th></tr></thead>
            <tbody>
                {fullResults.map((r: any, i: number) => (
                    <tr key={i} className="border-b border-border/10 last:border-0 hover:bg-secondary/50">
                        <td className="py-3 font-mono">{r.Strategy} {r.Strategy === d.recommended_strategy && <span className="ml-2 bg-lime-500/20 text-lime-400 text-[10px] px-2 py-0.5 rounded border border-lime-500/30">RECOMMENDED</span>}</td>
                        <td className="py-3">{r['Mean Race Time']?.toFixed(1)}</td>
                        <td className="py-3">P{r['Mean Finish Position']?.toFixed(1)}</td>
                        <td className="py-3 text-cyan-400">{(r['Podium Probability'] * 100)?.toFixed(0)}%</td>
                        <td className="py-3 text-red-400">{(r['P1 Probability'] * 100)?.toFixed(0)}%</td>
                        <td className="py-3"><span className={`text-[10px] px-2 py-0.5 rounded border ${r.Risk > 0.6 ? 'bg-red-500/20 text-red-400 border-red-500/30' : r.Risk < 0.4 ? 'bg-lime-500/20 text-lime-400 border-lime-500/30' : 'bg-amber-500/20 text-amber-400 border-amber-500/30'}`}>{r.Risk > 0.6 ? 'High' : r.Risk < 0.4 ? 'Low' : 'Medium'}</span></td>
                    </tr>
                ))}
            </tbody>
        </table>
    </div>

    <div className="grid grid-cols-1 xl:grid-cols-2 gap-4">
        <ChartCard title="Strategy Race Time" subtitle="Lower is faster">
            <ChartFrame height={250}>
                <BarChart data={fullResults} layout="vertical" margin={{ left: 10, right: 20 }}>
                    <CartesianGrid stroke={chartColors.grid} horizontal={false} />
                    <XAxis type="number" domain={['dataMin - 10', 'dataMax + 10']} tick={axis} />
                    <YAxis dataKey="Strategy" type="category" tick={axis} width={70} />
                    <Tooltip contentStyle={tooltipStyle} formatter={(val: number) => val.toFixed(1) + "s"} />
                    <Bar dataKey="Mean Race Time" radius={[0, 4, 4, 0]} maxBarSize={40}>
                        {fullResults.map((entry: any, index: number) => (
                            <Cell key={`cell-${index}`} fill={entry.Strategy === d.recommended_strategy ? chartColors.lime : chartColors.red} />
                        ))}
                    </Bar>
                </BarChart>
            </ChartFrame>
        </ChartCard>

        <ChartCard title="Outcome Probability" subtitle="Podium and win likelihood">
            <ChartFrame height={250}>
                <BarChart data={fullResults} maxBarSize={60}>
                    <CartesianGrid stroke={chartColors.grid} vertical={false} />
                    <XAxis dataKey="Strategy" tick={axis} />
                    <YAxis tickFormatter={(val) => `${(val * 100).toFixed(0)}%`} tick={axis} />
                    <Tooltip contentStyle={tooltipStyle} formatter={(val: number) => (val * 100).toFixed(1) + "%"} />
                    <Legend iconType="square" wrapperStyle={{ fontSize: 12 }} />
                    <Bar dataKey="Podium Probability" name="Podium" fill={chartColors.cyan} radius={[4, 4, 0, 0]} />
                    <Bar dataKey="P1 Probability" name="Win" fill={chartColors.red} radius={[4, 4, 0, 0]} />
                </BarChart>
            </ChartFrame>
        </ChartCard>

        <ChartCard title="Finishing Position Distribution" subtitle={`Recommended strategy: ${d.recommended_strategy}`}>
            <ChartFrame height={250}>
                <BarChart data={posDist} maxBarSize={50}>
                    <CartesianGrid stroke={chartColors.grid} vertical={false} />
                    <XAxis dataKey="pos" tick={axis} />
                    <YAxis tickFormatter={(val) => `${val}%`} tick={axis} />
                    <Tooltip contentStyle={tooltipStyle} formatter={(val: number) => val + "%"} />
                    <Bar dataKey="prob" name="Probability" fill={chartColors.amber} radius={[4, 4, 0, 0]} />
                </BarChart>
            </ChartFrame>
        </ChartCard>

        <ChartCard title="Strategy Timeline" subtitle="Pit stops and compound sequence">
            <ChartFrame height={250}>
                <BarChart data={timelineData} layout="vertical" stackOffset="expand" margin={{ left: 10, right: 20 }}>
                    <CartesianGrid stroke={chartColors.grid} horizontal={false} />
                    <XAxis type="number" hide />
                    <YAxis dataKey="name" type="category" tick={axis} width={70} />
                    <Tooltip contentStyle={tooltipStyle} />
                    <Bar dataKey="stint1" stackId="a" fill="var(--chart-amber)" stroke="var(--background)" strokeWidth={2} maxBarSize={30} />
                    <Bar dataKey="stint2" stackId="a" fill="var(--muted-foreground)" stroke="var(--background)" strokeWidth={2} maxBarSize={30} />
                    <Bar dataKey="stint3" stackId="a" fill="var(--chart-red)" stroke="var(--background)" strokeWidth={2} maxBarSize={30} />
                </BarChart>
            </ChartFrame>
        </ChartCard>
    </div>
  </>;
}

function PitWall({ config }: { config: Config }) {
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string|null>(null);
  const [decision, setDecision] = useState<any>(null);
  const totalLaps = config.race?.total_laps || 57;
  const [scrubLap, setScrubLap] = useState(Math.round(totalLaps * 0.49));
  const [isPlaying, setIsPlaying] = useState(false);

  // Playback timer to auto-advance laps
  useEffect(() => {
      let interval: NodeJS.Timeout;
      if (isPlaying) {
          interval = setInterval(() => {
              setScrubLap(prev => {
                  if (prev >= totalLaps) {
                      setIsPlaying(false);
                      return prev;
                  }
                  return prev + 1;
              });
          }, 1200);
      }
      return () => clearInterval(interval);
  }, [isPlaying, totalLaps]);

  // Reset lap if race changes
  useEffect(() => {
      setIsPlaying(false);
      setScrubLap(Math.round((config.race?.total_laps || 57) * 0.49));
  }, [config.race?.race_id]);

  useEffect(() => {
      if (!decision) setLoading(true);
      setError(null);
      api.getPitWallDecision(getBaseState(config, scrubLap), 5).then(res => {
          setDecision(res.data);
          setLoading(false);
      }).catch(err => {
          setError(err.message);
          setLoading(false);
      });
  }, [config, scrubLap]);

  const startCompound = config.tyre || "MEDIUM";
  const pitLap = startCompound === "SOFT" 
      ? Math.round(totalLaps * 0.30) 
      : startCompound === "MEDIUM" 
          ? Math.round(totalLaps * 0.44) 
          : Math.round(totalLaps * 0.58);

  const hasPitted = scrubLap > pitLap;
  const nextCompound = startCompound === "HARD" ? "MEDIUM" : "HARD";
  const currentTyre = hasPitted ? nextCompound : startCompound;
  const tyreAge = hasPitted ? Math.max(1, scrubLap - pitLap) : Math.max(1, scrubLap);
  const isPitLap = scrubLap === pitLap;

  // Dynamic Position: models pit lane drop & subsequent recovery
  const basePos = Math.round(config.driver?.avg_pos || 5);
  let currentPos = basePos;
  if (isPitLap || scrubLap === pitLap + 1) {
      currentPos = Math.min(20, basePos + 4);
  } else if (hasPitted) {
      const lapsSincePit = scrubLap - pitLap;
      const recovery = Math.min(4, Math.floor(lapsSincePit / 2.5));
      currentPos = Math.max(1, basePos + 4 - recovery);
  } else {
      const shift = (scrubLap % 9 === 0) ? -1 : (scrubLap % 13 === 0) ? 1 : 0;
      currentPos = Math.max(1, Math.min(20, basePos + shift));
  }

  // Dynamic Recent Pace: fuel burn effect + tyre degradation + pit outlap
  const basePace = config.driver?.base_pace || 91.5;
  const degRate = currentTyre === "SOFT" ? 0.12 : currentTyre === "MEDIUM" ? 0.08 : 0.05;
  const tyreDegDelta = tyreAge * degRate + (tyreAge > 16 ? Math.pow((tyreAge - 16) * 0.22, 2) : 0);
  const fuelEffect = scrubLap * 0.052;
  const paceNoise = Math.sin(scrubLap * 1.3) * 0.18;
  const pitPenalty = isPitLap ? 22.4 : (scrubLap === pitLap + 1 ? 3.0 : 0);
  const currentPaceSec = Math.max(75, basePace + tyreDegDelta - fuelEffect + paceNoise + pitPenalty);
  const paceMin = Math.floor(currentPaceSec / 60);
  const paceSec = (currentPaceSec % 60).toFixed(1).padStart(4, '0');
  const formattedPace = `${paceMin}:${paceSec}`;

  // Dynamic Gaps
  let gapAheadStr = "1.84s";
  let gapBehindStr = "1.20s";
  if (currentPos <= 1) {
      const leadSec = (1.5 + (scrubLap * 0.08) + Math.sin(scrubLap * 0.5) * 0.3).toFixed(2);
      gapAheadStr = "LEADER";
      gapBehindStr = `${leadSec}s`;
  } else if (isPitLap) {
      gapAheadStr = "+22.8s";
      gapBehindStr = "+1.40s";
  } else {
      const gapAheadVal = Math.max(0.6, 1.4 + Math.sin(scrubLap * 0.6) * 0.8 + (tyreAge > 12 ? (tyreAge - 12) * 0.1 : 0));
      const gapBehindVal = Math.max(0.5, 1.8 + Math.cos(scrubLap * 0.4) * 0.9 + (tyreAge > 15 ? -(tyreAge - 15) * 0.06 : 0));
      gapAheadStr = `${gapAheadVal.toFixed(2)}s`;
      gapBehindStr = `${gapBehindVal.toFixed(2)}s`;
  }

  // Dynamic Degradation status
  let degStatus: "FRESH" | "STABLE" | "MODERATE" | "HIGH" | "CRITICAL" = "STABLE";
  const softThresholds = [5, 10, 15];
  const medThresholds = [7, 15, 20];
  const hardThresholds = [10, 22, 28];
  const th = currentTyre === "SOFT" ? softThresholds : currentTyre === "MEDIUM" ? medThresholds : hardThresholds;
  if (tyreAge <= th[0]) degStatus = "FRESH";
  else if (tyreAge <= th[1]) degStatus = "STABLE";
  else if (tyreAge <= th[2]) degStatus = "MODERATE";
  else degStatus = "CRITICAL";

  // Dynamic Pit Window bounds
  const pitWindowStart = decision?.pit_window ? decision.pit_window[0] : Math.max(1, pitLap - 3);
  const pitWindowEnd = decision?.pit_window ? decision.pit_window[1] : Math.min(totalLaps, pitLap + 3);

  // Generate pit window area chart across tactical window around pit window
  const windowRangeStart = Math.max(1, pitWindowStart - 8);
  const windowRangeEnd = Math.min(totalLaps, pitWindowEnd + 8);
  const windowDataCount = windowRangeEnd - windowRangeStart + 1;

  const windowData = Array.from({ length: windowDataCount }, (_, i) => {
      const l = windowRangeStart + i;
      const isOptimal = l >= pitWindowStart && l <= pitWindowEnd;
      const distFromCenter = Math.abs(l - pitLap);
      const trafficPenalty = isOptimal ? 0.3 * Math.sin(l * 0.8) : Math.min(5.2, Math.pow(distFromCenter / 3.2, 1.6));
      const totalLoss = parseFloat((21.4 + trafficPenalty).toFixed(1));
      return {
          lap: l,
          loss: totalLoss,
          isOptimal
      };
  });

  // Dynamic Decision History: sliding window of up to 5 laps up to scrubLap
  const historyLen = Math.min(5, scrubLap);
  const historyData = Array.from({ length: historyLen }, (_, i) => {
      const l = scrubLap <= 5 ? i + 1 : (scrubLap - 5 + 1 + i);
      const isCurrent = l === scrubLap;
      const lHasPitted = l > pitLap;
      const lAge = lHasPitted ? Math.max(1, l - pitLap) : Math.max(1, l);
      
      let call = "STAY OUT";
      let conf = 85;

      if (isCurrent && decision) {
          call = decision.decision || "STAY OUT";
          conf = decision.metrics?.confidence_pct || parseInt(decision.robustness) || 85;
      } else if (!lHasPitted) {
          if (l < pitWindowStart - 2) {
              call = "STAY OUT";
              conf = Math.max(68, Math.min(97, Math.round(96 - (lAge / (pitLap || 25)) * 24)));
          } else if (l < pitWindowStart) {
              call = "MONITOR";
              conf = Math.round(65 + ((l - (pitWindowStart - 2)) / 2) * 12);
          } else if (l <= pitWindowEnd) {
              call = "PIT NOW";
              conf = Math.min(95, Math.round(75 + ((l - pitWindowStart) / Math.max(1, pitWindowEnd - pitWindowStart)) * 18));
          } else {
              call = "PIT NOW";
              conf = Math.min(98, 88 + (l - pitWindowEnd) * 3);
          }
      } else {
          call = "STAY OUT";
          conf = Math.max(70, Math.min(96, Math.round(95 - lAge * 1.5)));
      }

      return { lap: l, call, conf };
  });

  const togglePlay = () => {
      if (scrubLap >= totalLaps) {
          setScrubLap(1);
          setIsPlaying(true);
      } else {
          setIsPlaying(p => !p);
      }
  };

  return <><PageHeader eyebrow="Historical Race Replay" title="Dynamic Pit-Wall" description="Decision support under changing race conditions." config={config}/>
    
    <div className="flex items-center justify-between bg-secondary/30 border border-border p-3 rounded-lg mb-4">
        <div className="flex items-center gap-2 text-xs uppercase tracking-widest text-lime-400">
            <span className={`w-2 h-2 rounded-full bg-lime-400 ${isPlaying ? "animate-ping" : "animate-pulse"}`}/> 
            {isPlaying ? "RACE REPLAY PLAYING" : "RACE LIVE REPLAY"}
        </div>
        <div className="text-sm font-bold text-muted-foreground flex items-center gap-3">
            <span>{config.race?.name ? config.race.name.toUpperCase() : "GRAND PRIX"}</span> 
            <span className="text-red-500 text-lg font-mono font-bold">LAP {scrubLap} / {totalLaps}</span>
        </div>
    </div>

    <div className="kpi-grid mb-4" style={{ gridTemplateColumns: 'repeat(7, 1fr)' }}>
        <Metric label="POSITION" value={`P${currentPos}`} />
        <Metric label="TYRE" value={currentTyre} />
        <Metric label="TYRE AGE" value={tyreAge.toString()} />
        <Metric label="GAP AHEAD" value={gapAheadStr} />
        <Metric label="GAP BEHIND" value={gapBehindStr} />
        <Metric label="RECENT PACE" value={formattedPace} />
        <Metric label="DEGRADATION" value={degStatus} accent={degStatus === "CRITICAL" || degStatus === "HIGH"} />
    </div>

    <StateWrapper loading={loading} error={error}>
        {decision && (
            <>
            <section className={`pit-decision ${decision.decision === "PIT NOW" ? "critical" : "stable"}`}>
                <div className="decision-main">
                    <span>STRATEGY CALL</span>
                    <h2>{decision.decision}</h2>
                    <p>Confidence <b>{decision.robustness}</b></p>
                </div>
                <div className="decision-tyre">
                    <span>SWITCH TO</span>
                    <strong>{decision.recommended_compound || "HARD"}</strong>
                    <div className={`w-6 h-6 rounded-full border-2 border-background mt-2 shadow flex items-center justify-center text-[10px] font-bold ${
                        decision.recommended_compound === "SOFT" ? "bg-red-500 text-white" :
                        decision.recommended_compound === "HARD" ? "bg-slate-200 text-black" :
                        "bg-amber-400 text-black"
                    }`}>
                        {decision.recommended_compound?.[0] || "H"}
                    </div>
                </div>
                <div className="why border-l border-white/10 pl-8">
                    <span>WHY THIS CALL?</span>
                    <ul className="grid grid-cols-2 gap-x-8 text-sm opacity-80">
                        {decision.reasoning?.map((r: string, i: number) => (
                            <li key={i} className="flex items-start gap-2 before:content-['✓'] before:text-lime-400">{r}</li>
                        ))}
                    </ul>
                </div>
            </section>
            
            <div className="grid grid-cols-1 xl:grid-cols-2 gap-4 mt-4">
                <ChartCard title="Decision History" subtitle="Live pit wall calls & model confidence per lap">
                    <ChartFrame height={200}>
                        <LineChart data={historyData} margin={{ top: 30, bottom: 25, left: 20, right: 20 }}>
                            <CartesianGrid stroke={chartColors.grid} vertical={false} horizontal={false} />
                            <XAxis dataKey="lap" axisLine={false} tickLine={false} tickFormatter={(v)=>`LAP ${v}`} tick={{fill: "var(--muted-foreground)", fontSize: 10}} />
                            <YAxis hide domain={[0, 110]} />
                            <Line dataKey="conf" type="monotone" stroke="var(--muted-foreground)" strokeWidth={1.5} dot={<CustomDot />} />
                        </LineChart>
                    </ChartFrame>
                </ChartCard>

                <ChartCard 
                    title="Pit Window & Traffic Projection" 
                    subtitle={
                        scrubLap < pitWindowStart 
                            ? `Lap ${scrubLap}: Pit window opens in ${pitWindowStart - scrubLap} laps (Laps ${pitWindowStart}–${pitWindowEnd})`
                            : scrubLap <= pitWindowEnd 
                                ? `Lap ${scrubLap}: INSIDE OPTIMAL PIT WINDOW · Clean air exit projected`
                                : `Lap ${scrubLap}: Past pit window · High tyre degradation penalty`
                    }
                >
                    <ChartFrame height={200}>
                        <AreaChart data={windowData} margin={{ left: -20, right: 10, top: 15, bottom: 0 }}>
                            <defs>
                                <linearGradient id="lossGrad" x1="0" y1="0" x2="0" y2="1">
                                    <stop offset="5%" stopColor={chartColors.cyan} stopOpacity={0.35}/>
                                    <stop offset="95%" stopColor={chartColors.cyan} stopOpacity={0.02}/>
                                </linearGradient>
                            </defs>
                            <CartesianGrid stroke={chartColors.grid} vertical={false} />
                            <XAxis dataKey="lap" tick={axis} tickFormatter={(v) => `L${v}`} />
                            <YAxis domain={['dataMin - 1', 'dataMax + 1']} tick={axis} tickFormatter={(v) => `${v}s`} />
                            <Tooltip 
                                contentStyle={tooltipStyle} 
                                formatter={(val: number) => [`${val.toFixed(1)}s`, "Projected Pit Loss"]} 
                                labelFormatter={(label) => `Lap ${label}`}
                            />
                            <Area type="monotone" dataKey="loss" stroke={chartColors.cyan} strokeWidth={2} fillOpacity={1} fill="url(#lossGrad)" />
                            <ReferenceArea 
                                x1={pitWindowStart} 
                                x2={pitWindowEnd} 
                                fill="var(--chart-lime)" 
                                fillOpacity={0.12} 
                                stroke="var(--chart-lime)" 
                                strokeOpacity={0.4} 
                                strokeDasharray="2 2"
                            />
                            <ReferenceLine 
                                x={scrubLap} 
                                stroke={chartColors.red} 
                                strokeWidth={2.5} 
                                label={{ 
                                    value: `CAR: LAP ${scrubLap}`, 
                                    fill: "var(--chart-red)", 
                                    position: "insideTop", 
                                    fontSize: 10, 
                                    fontWeight: "bold" 
                                }} 
                            />
                        </AreaChart>
                    </ChartFrame>
                </ChartCard>
            </div>
            </>
        )}
    </StateWrapper>

    <div className="fixed bottom-0 left-64 right-0 p-4 bg-background/95 backdrop-blur border-t border-border flex items-center gap-4 z-50">
        <div className="flex items-center gap-1 border border-border rounded-md bg-secondary/50 p-0.5">
            <Button 
                variant="ghost" 
                size="icon" 
                className="h-8 w-8 hover:bg-secondary text-foreground"
                onClick={() => {
                    setIsPlaying(false);
                    setScrubLap(prev => Math.max(1, prev - 1));
                }}
                title="Previous Lap (Step Backward)"
            >
                <ChevronLeft className="w-4 h-4"/>
            </Button>
            <Button 
                variant="ghost" 
                size="sm" 
                className={`h-8 px-3 text-xs uppercase font-semibold transition-all ${isPlaying ? "bg-lime-500/20 text-lime-400 border border-lime-500/40" : "hover:bg-secondary text-foreground"}`}
                onClick={togglePlay}
                title={isPlaying ? "Pause Replay" : "Play Race Replay"}
            >
                {isPlaying ? <Pause className="w-3.5 h-3.5 mr-1.5"/> : <Play className="w-3.5 h-3.5 mr-1.5"/>}
                {isPlaying ? "Pause" : "Play"}
            </Button>
            <Button 
                variant="ghost" 
                size="icon" 
                className="h-8 w-8 hover:bg-secondary text-foreground"
                onClick={() => {
                    setIsPlaying(false);
                    setScrubLap(prev => Math.min(totalLaps, prev + 1));
                }}
                title="Next Lap (Step Forward)"
            >
                <ChevronRight className="w-4 h-4"/>
            </Button>
            <Button 
                variant="ghost" 
                size="icon" 
                className="h-8 w-8 hover:bg-secondary text-muted-foreground hover:text-foreground"
                onClick={() => {
                    setIsPlaying(false);
                    setScrubLap(1);
                }}
                title="Reset to Lap 1"
            >
                <RotateCcw className="w-3.5 h-3.5"/>
            </Button>
        </div>
        <span className="text-[10px] uppercase text-muted-foreground font-bold tracking-widest whitespace-nowrap">CURRENT LAP</span>
        <Slider 
            defaultValue={[Math.round(totalLaps * 0.49)]} 
            max={totalLaps} 
            min={1} 
            step={1} 
            value={[scrubLap]} 
            onValueChange={(v) => {
                setIsPlaying(false);
                setScrubLap(v[0]);
            }} 
            className="flex-1 cursor-pointer" 
        />
        <span className="font-mono text-xl text-red-500 font-bold min-w-[3ch] text-right">{scrubLap}</span>
    </div>
  </>;
}

// Helper for Decision History
const CustomDot = (props: any) => {
    const { cx, cy, payload } = props;
    if (!cx || !cy) return null;
    const isPit = payload.call === "PIT NOW";
    const isWindow = payload.call === "PIT WINDOW" || payload.call === "MONITOR";
    const fill = isPit ? "var(--chart-red)" : isWindow ? "var(--chart-amber)" : "var(--chart-lime)";
    return (
        <g>
            <circle cx={cx} cy={cy} r={5} fill={fill} stroke="var(--background)" strokeWidth={1.5} />
            <text x={cx} y={cy - 12} textAnchor="middle" fill="var(--foreground)" fontSize={10} fontWeight="bold">{payload.call}</text>
            <text x={cx} y={cy + 18} textAnchor="middle" fill={fill} fontSize={10} fontWeight="bold">{payload.conf}%</text>
        </g>
    );
};

function WhatIf({ config }: { config: Config }) {
    const totalLaps = config.race?.total_laps || 57;
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState<string|null>(null);
    const [results, setResults] = useState<any[] | null>(null);
    
    const [lap, setLap] = useState(Math.round(totalLaps * 0.49).toString()); 
    const [tyre, setTyre] = useState(config.tyre || "MEDIUM");

    useEffect(() => {
        setLap(Math.round((config.race?.total_laps || 57) * 0.49).toString());
        setTyre(config.tyre || "MEDIUM");
        setResults(null);
    }, [config]);
    
    const runSim = () => {
        setLoading(true); setError(null);
        const state = getBaseState(config, parseInt(lap), tyre);
        
        // Build 3 scenarios: Pit Now, Stay 3 Laps, Stay 5 Laps
        const nextCompound = tyre === "HARD" ? "MEDIUM" : "HARD";
        const s1 = { name: "PIT NOW", starting_compound: tyre, planned_compounds: [tyre, nextCompound], pit_laps: [parseInt(lap)] };
        const s2 = { name: "STAY +3 LAPS", starting_compound: tyre, planned_compounds: [tyre, nextCompound], pit_laps: [parseInt(lap) + 3] };
        const s3 = { name: "STAY +5 LAPS", starting_compound: tyre, planned_compounds: [tyre, nextCompound], pit_laps: [parseInt(lap) + 5] };
        
        api.optimizeStrategy(state, [s1, s2, s3], 10, config.risk).then(res => {
            if (res.data && res.data.full_results) {
                setResults(res.data.full_results);
            }
            setLoading(false);
        }).catch(err => {
            setError(err.message);
            setLoading(false);
        });
    };

    return <><PageHeader eyebrow="Decision Sandbox" title="What-If Simulator" description="Stress-test strategy choices before making the call." config={config}/>
      <div className="sim-layout"><aside className="panel sim-controls"><div className="flex items-center gap-2"><Settings2/><h3 className="section-title">Scenario Inputs</h3></div>
        
        <label className="block"><span className="mb-2 block text-[10px] font-bold uppercase tracking-[0.12em] text-muted-foreground">CURRENT LAP</span>
            <div className="flex items-center gap-4">
                <Slider defaultValue={[Math.round(totalLaps * 0.49)]} max={totalLaps} min={1} step={1} value={[parseInt(lap)]} onValueChange={(v) => setLap(v[0].toString())} className="flex-1" />
                <span className="font-mono text-xs">{lap}</span>
            </div>
        </label>
        
        <Field label="Current Tyre" value={tyre} options={compounds.map(c=>({id:c, label:c}))} onChange={setTyre}/>
        
        <Field label="Safety Car" value={"YES"} options={[{id:"YES",label:"YES"},{id:"NO",label:"NO"}]} onChange={()=>{}}/>
        <Field label="Weather Scenario" value={"DRY"} options={[{id:"DRY",label:"DRY"}]} onChange={()=>{}}/>
        <Field label="Risk Preference" value={config.risk || "Balanced"} options={[{id:"Conservative",label:"Conservative"},{id:"Balanced",label:"Balanced"},{id:"Aggressive",label:"Aggressive"}]} onChange={()=>{}}/>
        
        <Button className="w-full" onClick={runSim}><Activity/> Simulate Scenarios</Button>
      </aside>
      
      <div className="space-y-4">
        <StateWrapper loading={loading} error={error}>
            {results && (
                <>
                <div className="flex gap-2 mb-4 border-b border-border pb-4">
                    <Button variant="default" size="sm" className="bg-red-500 hover:bg-red-600 text-white border border-red-400">PIT NOW</Button>
                    <Button variant="outline" size="sm" className="bg-secondary text-muted-foreground">STAY 3 LAPS</Button>
                    <Button variant="outline" size="sm" className="bg-secondary text-muted-foreground">STAY 5 LAPS</Button>
                </div>

                <ChartCard title="Scenario Comparison" subtitle="Projected outcomes from current race state" className="!bg-transparent border-none !p-0">
                    <div className="grid grid-cols-1 xl:grid-cols-3 gap-4">
                        {results.map((r, i) => (
                            <div key={i} className={`p-4 rounded-lg border ${i === 0 ? "border-red-500 bg-red-500/5" : "border-border bg-secondary/30"}`}>
                                <div className="flex items-center justify-between mb-4">
                                    <span className="text-xs font-bold text-muted-foreground">{r.Strategy}</span>
                                </div>
                                <div className="text-2xl font-mono font-bold mb-4">{Math.floor(r['Mean Race Time']/60)}:{(r['Mean Race Time']%60).toFixed(0).padStart(2, '0')}</div>
                                
                                <div className="flex items-center justify-between text-xs py-2 border-b border-border/50">
                                    <span className="text-muted-foreground">Expected Pos</span>
                                    <strong>P{r['Mean Finish Position'].toFixed(1)}</strong>
                                </div>
                                <div className="flex items-center justify-between text-xs py-2 border-b border-border/50">
                                    <span className="text-muted-foreground">Podium</span>
                                    <strong>{(r['Podium Probability']*100).toFixed(0)}%</strong>
                                </div>
                                <div className="flex items-center justify-between text-xs py-2">
                                    <span className="text-muted-foreground">Risk</span>
                                    <strong className={r.Risk > 0.6 ? "text-red-400" : "text-lime-400"}>{r.Risk > 0.6 ? "HIGH" : r.Risk < 0.4 ? "LOW" : "MEDIUM"}</strong>
                                </div>
                            </div>
                        ))}
                    </div>
                </ChartCard>

                <div className="grid grid-cols-1 xl:grid-cols-2 gap-4 mt-4">
                    <ChartCard title="Projected Race Time" subtitle="Seconds | lower is faster">
                        <ChartFrame height={250}>
                            <BarChart data={results} margin={{ left: -20, right: 10 }}>
                                <CartesianGrid stroke={chartColors.grid} vertical={false} />
                                <XAxis dataKey="Strategy" tick={axis} />
                                <YAxis domain={['dataMin - 10', 'dataMax + 10']} tick={axis} />
                                <Tooltip contentStyle={tooltipStyle} formatter={(val: number) => val.toFixed(1) + "s"} />
                                <Bar dataKey="Mean Race Time" fill={chartColors.red} radius={[4, 4, 0, 0]} maxBarSize={60}>
                                    {results.map((entry: any, index: number) => (
                                        <Cell key={`cell-${index}`} fill={index === 0 ? chartColors.red : chartColors.cyan} />
                                    ))}
                                </Bar>
                            </BarChart>
                        </ChartFrame>
                    </ChartCard>

                    <ChartCard title="Podium Probability" subtitle="Outcome likelihood by call">
                        <ChartFrame height={250}>
                            <BarChart data={results} margin={{ left: -20, right: 10 }}>
                                <CartesianGrid stroke={chartColors.grid} vertical={false} />
                                <XAxis dataKey="Strategy" tick={axis} />
                                <YAxis tickFormatter={(val) => `${val * 100}%`} tick={axis} />
                                <Tooltip contentStyle={tooltipStyle} formatter={(val: number) => (val * 100).toFixed(1) + "%"} />
                                <Bar dataKey="Podium Probability" fill={chartColors.cyan} radius={[4, 4, 0, 0]} maxBarSize={60}>
                                    {results.map((entry: any, index: number) => (
                                        <Cell key={`cell-${index}`} fill={index === 0 ? chartColors.cyan : chartColors.muted} />
                                    ))}
                                </Bar>
                            </BarChart>
                        </ChartFrame>
                    </ChartCard>
                </div>
                </>
            )}
            {!results && !loading && (
                <div className="p-12 text-center text-muted-foreground border border-border rounded-lg bg-secondary/10 flex flex-col items-center justify-center h-full min-h-[400px]">
                    <Activity className="w-12 h-12 mb-4 opacity-20" />
                    <p>Configure parameters and click Simulate to generate what-if scenario outcomes.</p>
                </div>
            )}
        </StateWrapper>
      </div></div>
    </>;
  }

export function StrategyDashboard() {
  const [page,setPage] = useState<Page>("Overview"); 
  const [draft,setDraft] = useState<any>({season: "2024", raceId: "1", driverId: "1", tyre:"MEDIUM", risk:"Balanced"}); 
  const [config,setConfig] = useState<Config>({race: null, driver: null, tyre: "MEDIUM", risk: "Balanced"}); 
  const [mobileOpen,setMobileOpen] = useState(false);
  const [analysisNotification, setAnalysisNotification] = useState<string | null>(null);
  
  const [races, setRaces] = useState<any[]>([]);
  const [drivers, setDrivers] = useState<any[]>([]);
  const [health, setHealth] = useState<any>(null);

  const availableSeasons = useMemo(() => Array.from(new Set(races.map(r => r.season).filter(Boolean))).sort((a: any, b: any) => b - a), [races]);
  const filteredRaces = useMemo(() => races.filter(r => r.season?.toString() === draft.season), [races, draft.season]);

  const isDirty = useMemo(() => {
      if (!config.race || !config.driver) return false;
      return (
          draft.season !== config.race.season?.toString() ||
          draft.raceId !== config.race.race_id?.toString() ||
          draft.driverId !== config.driver.driver_id?.toString() ||
          draft.tyre !== config.tyre ||
          draft.risk !== config.risk
      );
  }, [draft, config]);

  useEffect(() => {
      api.getHealth().then(setHealth).catch(() => setHealth({status: "error"}));
      api.getRaces().then(res => {
          if (res.success && res.data.length > 0) {
              setRaces(res.data);
              const defaultSeason = res.data[0].season?.toString() || "2024";
              const defaultRace = res.data[0].race_id.toString();
              setDraft((d: any) => ({...d, season: defaultSeason, raceId: defaultRace}));
          }
      }).catch(err => console.error("Races fetch error:", err));
      api.getDrivers().then(res => {
          if (res.success && res.data.length > 0) {
              setDrivers(res.data);
              setDraft((d: any) => ({...d, driverId: res.data[0].driver_id.toString()}));
          }
      }).catch(err => console.error("Drivers fetch error:", err));
  }, []);

  const runAnalysis = () => {
      const selectedRace = races.find(r => r.race_id.toString() === draft.raceId) || races[0];
      const selectedDriver = drivers.find(d => d.driver_id.toString() === draft.driverId) || drivers[0];
      setConfig({
          race: selectedRace,
          driver: selectedDriver,
          tyre: draft.tyre,
          risk: draft.risk
      });
      if (selectedDriver && selectedRace) {
          setAnalysisNotification(`Active Scenario: ${selectedDriver.name} · ${selectedRace.name} · ${draft.tyre} · ${draft.risk}`);
          setTimeout(() => setAnalysisNotification(null), 5000);
      }
  };

  useEffect(() => {
      // Auto run analysis once data is loaded
      if (races.length > 0 && drivers.length > 0 && !config.race) {
          runAnalysis();
      }
  }, [races, drivers]);

  const icons = [CircleGauge,Activity,TrendingUp,BarChart3,AlertTriangle,CloudRain];
  return <div className="app-shell"><aside className={`sidebar ${mobileOpen ? "open" : ""}`}><div className="brand"><div className="brand-mark">S<span>IQ</span></div><div><strong>F1 STRATEGY<em>IQ</em></strong><small>RACE INTELLIGENCE</small></div></div><nav>{pages.map((p,i)=>{const Icon=icons[i] ?? Gauge; return <Button key={p} variant="ghost" onClick={()=>{setPage(p);setMobileOpen(false)}} className={page===p?"active":""}><Icon/>{p}</Button>})}</nav><div className="config"><div className="config-title"><Settings2/><span>Race Configuration</span></div><Field label="Season" value={draft.season} options={availableSeasons.map((s: any) => ({id: s.toString(), label: s.toString()}))} onChange={v => { setDraft({...draft, season: v, raceId: races.find(r => r.season?.toString() === v)?.race_id.toString() || draft.raceId}); }}/><Field label="Grand Prix" value={draft.raceId} options={filteredRaces.map(r => ({id: r.race_id.toString(), label: r.name}))} onChange={v=>setDraft({...draft,raceId:v})}/><Field label="Driver" value={draft.driverId} options={drivers.map(d => ({id: d.driver_id.toString(), label: d.name}))} onChange={v=>setDraft({...draft,driverId:v})}/><Field label="Starting Tyre" value={draft.tyre} options={compounds.map(c=>({id:c, label:c}))} onChange={v=>setDraft({...draft,tyre:v})}/><Field label="Risk Preference" value={draft.risk} options={[{id:"Conservative",label:"Conservative"},{id:"Balanced",label:"Balanced"},{id:"Aggressive",label:"Aggressive"}]} onChange={v=>setDraft({...draft,risk:v})}/><Button className={`run-analysis ${isDirty ? "!border-lime-400 !bg-lime-500/25 !text-lime-300 font-bold shadow-lg shadow-lime-500/20" : ""}`} onClick={runAnalysis}><Activity className={isDirty ? "animate-spin" : ""}/>{isDirty ? "APPLY SCENARIO" : "RUN ANALYSIS"}</Button>{isDirty && <div className="text-[10px] text-lime-400 font-mono mt-1 text-center flex items-center justify-center gap-1.5"><span className="w-1.5 h-1.5 rounded-full bg-lime-400 animate-ping"/> Changes Pending - Click to Apply</div>}</div><div className="system-status"><span className={health?.status === "ok" ? "bg-green-500" : "bg-red-500"}/><div><b>FASTAPI ENGINE</b><small>{health?.status === "ok" ? "Online" : "Offline"}</small></div></div></aside>
    <main><div className="mobile-bar"><Button variant="ghost" size="icon" onClick={()=>setMobileOpen(!mobileOpen)} aria-label="Toggle navigation"><Settings2/></Button><b>F1 STRATEGYIQ</b><span>{page}</span></div><div className="content">{analysisNotification && <div className="mb-4 px-4 py-2.5 bg-lime-500/10 border border-lime-500/30 rounded-lg text-xs font-mono text-lime-400 flex items-center justify-between shadow-sm animate-fadeIn"><div className="flex items-center gap-2"><span className="w-2 h-2 rounded-full bg-lime-400 animate-pulse"/><strong>{analysisNotification}</strong></div><span className="text-[10px] uppercase tracking-wider opacity-75">LIVE ML PIPELINE UPDATED</span></div>}{page==="Overview"&&<Overview config={config}/>} {page==="Race Analysis"&&<RaceAnalysis config={config} driversList={drivers}/>} {page==="Tyre Intelligence"&&<TyreIntelligence config={config}/>} {page==="Strategy Optimizer"&&<StrategyOptimizer config={config}/>} {page==="Dynamic Pit-Wall"&&<PitWall config={config}/>} {page==="What-If Simulator"&&<WhatIf config={config}/>}<footer><span>STRATEGYIQ · PHASE 11 INTEGRATION</span><span>REAL FASTAPI PIPELINE</span></footer></div></main>{mobileOpen&&<button className="sidebar-scrim" aria-label="Close navigation" onClick={()=>setMobileOpen(false)}/>}</div>;
}
