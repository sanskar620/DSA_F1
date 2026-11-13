import os
import sys
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, KeepTogether, HRFlowable
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.pdfgen import canvas

class NumberedCanvas(canvas.Canvas):
    """
    Two-pass canvas to dynamically compute total pages and render running headers and footers.
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_decorations(num_pages)
            super().showPage()
        super().save()

    def draw_page_decorations(self, page_count):
        if self._pageNumber == 1:
            return  # Suppress running header/footer on cover page
        self.saveState()
        self.setFont("Helvetica-Bold", 8)
        self.setFillColor(colors.HexColor("#475569"))
        
        # Running Top Header
        self.drawString(54, 11 * 72 - 36, "F1 STRATEGYIQ: END-TO-END MASTER SPECIFICATION")
        self.setFont("Helvetica", 8)
        self.drawRightString(8.5 * 72 - 54, 11 * 72 - 36, "DSA & MACHINE LEARNING PLATFORM")
        self.setStrokeColor(colors.HexColor("#CBD5E1"))
        self.setLineWidth(0.75)
        self.line(54, 11 * 72 - 42, 8.5 * 72 - 54, 11 * 72 - 42)
        
        # Running Bottom Footer
        self.line(54, 46, 8.5 * 72 - 54, 46)
        self.setFont("Helvetica", 8)
        self.setFillColor(colors.HexColor("#64748B"))
        self.drawString(54, 32, "Formula 1 Strategic Decision Support System • Capstone Project")
        page_text = f"Page {self._pageNumber} of {page_count}"
        self.drawRightString(8.5 * 72 - 54, 32, page_text)
        self.restoreState()

def build_pdf(filename="F1_StrategyIQ_Master_Project_Report.pdf"):
    doc = SimpleDocTemplate(
        filename,
        pagesize=letter,
        leftMargin=54,
        rightMargin=54,
        topMargin=54,
        bottomMargin=54
    )

    styles = getSampleStyleSheet()
    
    # Custom Palette
    c_primary = colors.HexColor("#E10600")      # F1 Racing Red
    c_dark = colors.HexColor("#0F172A")         # Deep Slate / Navy
    c_text = colors.HexColor("#1E293B")         # Charcoal Body
    c_muted = colors.HexColor("#64748B")        # Muted Slate
    c_card_bg = colors.HexColor("#F8FAFC")      # Card Light Gray
    c_border = colors.HexColor("#E2E8F0")       # Border Line

    # Typography Styles
    cover_tag = ParagraphStyle(
        'CoverTag',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=11,
        leading=14,
        textColor=c_primary,
        spaceAfter=6
    )

    title_style = ParagraphStyle(
        'CoverTitle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=26,
        leading=32,
        textColor=c_dark,
        spaceAfter=10
    )

    subtitle_style = ParagraphStyle(
        'CoverSubtitle',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=12,
        leading=17,
        textColor=c_muted,
        spaceAfter=20
    )

    h1_style = ParagraphStyle(
        'Heading1_Custom',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=14,
        leading=18,
        textColor=c_dark,
        spaceBefore=14,
        spaceAfter=6,
        keepWithNext=True
    )

    h2_style = ParagraphStyle(
        'Heading2_Custom',
        parent=styles['Heading2'],
        fontName='Helvetica-Bold',
        fontSize=11,
        leading=15,
        textColor=c_primary,
        spaceBefore=8,
        spaceAfter=4,
        keepWithNext=True
    )

    body_style = ParagraphStyle(
        'Body_Custom',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9,
        leading=13.5,
        textColor=c_text,
        spaceAfter=6
    )

    bullet_style = ParagraphStyle(
        'Bullet_Custom',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=8.8,
        leading=13,
        textColor=c_text,
        leftIndent=12,
        firstLineIndent=-8,
        spaceAfter=3.5
    )

    callout_style = ParagraphStyle(
        'Callout_Text',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=8.8,
        leading=13,
        textColor=c_dark
    )

    story = []

    # =========================================================================
    # COVER PAGE
    # =========================================================================
    story.append(Spacer(1, 30))
    story.append(Paragraph("FORMULA 1 • STRATEGY OPTIMIZATION PLATFORM", cover_tag))
    story.append(Paragraph("F1 StrategyIQ: Data-Driven Race Strategy Optimization & Dynamic Pit-Wall System", title_style))
    story.append(Paragraph("End-to-End Master Project Documentation: Theoretical Foundations, Data Structures & Algorithms, Machine Learning Telemetry, and Cloud Production Deployment", subtitle_style))
    story.append(HRFlowable(width="100%", thickness=2.5, color=c_primary, spaceBefore=4, spaceAfter=18))

    meta_data = [
        [Paragraph("<b>Project Domain:</b>", body_style), Paragraph("Data Structures & Algorithms (DSA), Applied Machine Learning, Full-Stack Distributed Systems", body_style)],
        [Paragraph("<b>Lead Developer:</b>", body_style), Paragraph("Sanskar (DSA Project / Capstone Portfolio)", body_style)],
        [Paragraph("<b>Technical Stack:</b>", body_style), Paragraph("Python 3.11, FastAPI, React 19, TypeScript, PostgreSQL, XGBoost, Scikit-Learn, Vite, Tailwind CSS", body_style)],
        [Paragraph("<b>Production Hosting:</b>", body_style), Paragraph("Frontend on Vercel • Backend & PostgreSQL Database on Render Cloud", body_style)],
        [Paragraph("<b>Open-Source Repositories:</b>", body_style), Paragraph("https://github.com/sanskar620/DSA_F1 • https://github.com/sanskar620/strategyiq", body_style)],
        [Paragraph("<b>Documentation Version:</b>", body_style), Paragraph("Release v2.0 Production • November 2026", body_style)]
    ]
    meta_table = Table(meta_data, colWidths=[130, 374])
    meta_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), c_card_bg),
        ('BOX', (0,0), (-1,-1), 1, c_border),
        ('INNERGRID', (0,0), (-1,-1), 0.5, c_border),
        ('TOPPADDING', (0,0), (-1,-1), 5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 5),
        ('LEFTPADDING', (0,0), (-1,-1), 8),
        ('RIGHTPADDING', (0,0), (-1,-1), 8),
    ]))
    story.append(meta_table)

    story.append(Spacer(1, 20))

    exec_text = (
        "<b>Executive Abstract:</b> Modern Formula 1 racing operates on razor-thin tactical margins where a two-second error "
        "in pit timing or traffic re-entry can demote a front-runner from a race win to outside the top five. <b>F1 StrategyIQ</b> is "
        "an enterprise-grade tactical intelligence platform that merges mathematical optimization, causal machine learning, "
        "and discrete-time race simulation. By modeling non-linear tyre thermal degradation, stochastic traffic drag, dynamic competitor "
        "pace, and FIA regulatory mandates across 67,204 historical telemetry laps and 1,000 Monte Carlo iterations, the platform "
        "derives Pareto-optimal stint strategies and sub-second pit-wall decision support delivered via an interactive web dashboard."
    )
    exec_table = Table([[Paragraph(exec_text, callout_style)]], colWidths=[504])
    exec_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#EFF6FF")),
        ('BOX', (0,0), (-1,-1), 1, colors.HexColor("#BFDBFE")),
        ('LINELEFT', (0,0), (-1,-1), 3.5, c_primary),
        ('TOPPADDING', (0,0), (-1,-1), 8),
        ('BOTTOMPADDING', (0,0), (-1,-1), 8),
        ('LEFTPADDING', (0,0), (-1,-1), 10),
        ('RIGHTPADDING', (0,0), (-1,-1), 10),
    ]))
    story.append(exec_table)

    story.append(PageBreak())

    # =========================================================================
    # SECTION 1: INTRODUCTION & BACKGROUND
    # =========================================================================
    story.append(Paragraph("1. Introduction & Domain Background", h1_style))
    story.append(HRFlowable(width="100%", thickness=1, color=c_primary, spaceBefore=2, spaceAfter=6))
    story.append(Paragraph(
        "Formula 1 represents the pinnacle of international motorsport engineering. While vehicle aerodynamic efficiency, engine thermal power, "
        "and driver mechanical skill are foundational, modern Grands Prix are frequently won or lost from the pit-wall. A race strategy involves "
        "determining the exact lap to pit, the sequential tyre compound selection (Soft, Medium, Hard), fuel burn profiles, and tactical responses "
        "to track neutralizations such as Safety Cars (SC) or Virtual Safety Cars (VSC).",
        body_style
    ))
    story.append(Paragraph(
        "Historically, strategy tools relied on simple deterministic lap-time averages. However, deterministic simulations fundamentally break down "
        "under live racing conditions because racing is stochastic: traffic blocks overtakes, dirty air degrades aerodynamic downforce, pit crews "
        "exhibit human variance (&plusmn;1.2s), and competitor undercuts dynamically reshape track position. <b>F1 StrategyIQ</b> was built to solve "
        "these multi-variable challenges through a synergy of <b>Data Structures & Algorithms (DSA)</b>, <b>Machine Learning</b>, and <b>Monte Carlo simulations</b>.",
        body_style
    ))

    # =========================================================================
    # SECTION 2: PROBLEM STATEMENT & MOTIVATION
    # =========================================================================
    story.append(Paragraph("2. Problem Statement & Mathematical Challenges", h1_style))
    story.append(HRFlowable(width="100%", thickness=1, color=c_primary, spaceBefore=2, spaceAfter=6))
    story.append(Paragraph(
        "The mathematical objective of an F1 race strategy is to minimize total race completion duration <i>T</i><sub>race</sub> while maximizing "
        "expected finishing position <i>P</i><sub>finish</sub> under strict regulatory, physical, and tactical constraints:",
        body_style
    ))
    story.append(Paragraph("• <b>FIA Regulatory Constraints:</b> In a dry race, every classified car must use at least two distinct tyre compounds (e.g., Medium &rarr; Hard).", bullet_style))
    story.append(Paragraph("• <b>Non-Linear Compound Degradation:</b> Tyres do not degrade along a flat line. They exhibit initial bedding, followed by a linear degradation slope, terminating in an exponential thermal 'cliff' where lap times drop by >1.5s per lap.", bullet_style))
    story.append(Paragraph("• <b>Traffic Turbulence & Dirty Air:</b> Pitting incurs a ~22-25s pit lane transit delta. Re-entering behind a slower car costs 0.8s - 1.4s per lap in aerodynamic wake turbulence, severely damaging overtaking prospects.", bullet_style))
    story.append(Paragraph("• <b>Stochastic Outcome Distribution:</b> An aggressive strategy that is faster on paper but highly sensitive to traffic has a dangerous risk variance compared to a robust, flexible strategy.", bullet_style))

    # =========================================================================
    # SECTION 3: SYSTEM PRINCIPLES & ROADMAP
    # =========================================================================
    story.append(Paragraph("3. Architectural Philosophy & Phase Breakdown", h1_style))
    story.append(HRFlowable(width="100%", thickness=1, color=c_primary, spaceBefore=2, spaceAfter=6))
    story.append(Paragraph(
        "The project is structured around an immutable operational paradigm: "
        "<b>ANALYZE &rarr; PREDICT &rarr; SIMULATE &rarr; OPTIMIZE &rarr; DECIDE &rarr; RE-EVALUATE</b>.",
        body_style
    ))

    loop_data = [
        ["Phase", "Component", "Primary Algorithmic / Engineering Function"],
        ["Phases 1-2", "Data Ingestion & DB", "PostgreSQL relational schema design, FastF1 & Jolpica pipeline ETL."],
        ["Phases 3-4", "Cleaning & Feature Engineering", "Chronological ordering, proxy fuel-burn feature extraction, zero data leakage."],
        ["Phase 5", "Machine Learning Pipeline", "Trained XGBoost lap regressor, compound wear curves, pit-window classifier."],
        ["Phase 6", "Deterministic Simulator", "Discrete-time lap-by-lap race state transition model."],
        ["Phase 7", "Monte Carlo Engine", "1,000 stochastic runs evaluating empirical pace residuals & pit variance."],
        ["Phase 8", "Optimization Engine", "Pareto multi-objective frontier balancing expected race time vs. finish position."],
        ["Phase 9", "Dynamic Pit-Wall & What-If", "Tactical perturbation analysis (Pit Now vs Stay 3 vs Stay 5 Laps)."],
        ["Phases 10-11", "Full-Stack Deployment", "FastAPI REST API (Render) & React 19 interactive frontend (Vercel)."]
    ]
    t_loop = Table(loop_data, colWidths=[65, 130, 309])
    t_loop.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), c_dark),
        ('TEXTCOLOR', (0,0), (-1,0), colors.white),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('FONTSIZE', (0,0), (-1,-1), 7.5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 3),
        ('TOPPADDING', (0,0), (-1,-1), 3),
        ('GRID', (0,0), (-1,-1), 0.5, c_border),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, c_card_bg]),
    ]))
    story.append(t_loop)

    # =========================================================================
    # SECTION 4: DATA ENGINEERING & DATABASE
    # =========================================================================
    story.append(Spacer(1, 4))
    story.append(Paragraph("4. Data Engineering & PostgreSQL Schema Architecture", h1_style))
    story.append(HRFlowable(width="100%", thickness=1, color=c_primary, spaceBefore=2, spaceAfter=6))
    story.append(Paragraph(
        "A major challenge in motorsport analytics is data fragmentation across sessions. Historical lap times, compound stints, weather conditions, "
        "and track geometry originate from disparate telemetry feeds. A robust relational schema was designed in PostgreSQL to enforce referential "
        "integrity and sub-millisecond query execution:",
        body_style
    ))
    story.append(Paragraph("• <b>races:</b> Circuit identifier, official Grand Prix name, season, round, total laps, and geographic venue.", bullet_style))
    story.append(Paragraph("• <b>drivers & constructors:</b> Driver nationality, permanent code, constructor lineage, and aerodynamic profile.", bullet_style))
    story.append(Paragraph("• <b>laps:</b> Lap-by-lap telemetry tracking lap_time_seconds, sector 1/2/3 durations, on-track position, and pit status.", bullet_style))
    story.append(Paragraph("• <b>tyre_stints:</b> Tracked compound usage (Soft, Medium, Hard), stint sequence, start/end lap, and tyre age.", bullet_style))
    story.append(Paragraph("• <b>weather:</b> Real-time environmental tracking: TrackTemp (&deg;C), AirTemp (&deg;C), Humidity (%), WindSpeed, and Rainfall flag.", bullet_style))
    story.append(Paragraph(
        "<b>Addressing Unobservable Telemetry (Fuel Proxies):</b> In Formula 1, vehicle fuel load and fuel-flow maps are proprietary trade secrets. "
        "Inventing arbitrary fuel numbers compromises algorithmic validity. The platform uses <i>Lap Progress Ratio</i> (<i>L<sub>i</sub></i> / <i>L</i><sub>total</sub>) "
        "as a mathematically defensible fuel-burn proxy, representing the monotonic mass loss of ~100 kg down to 0 kg across the race distance.",
        body_style
    ))

    # =========================================================================
    # SECTION 5: MACHINE LEARNING PIPELINE (PHASE 5)
    # =========================================================================
    story.append(Paragraph("5. Machine Learning Telemetry Engine (Phase 5)", h1_style))
    story.append(HRFlowable(width="100%", thickness=1, color=c_primary, spaceBefore=2, spaceAfter=6))
    story.append(Paragraph(
        "Three specialized, leakage-safe machine learning pipelines were developed using <b>Scikit-Learn</b> and <b>XGBoost</b>, trained on "
        "67,204 validated historical laps across 63 Grands Prix:",
        body_style
    ))

    ml_data = [
        ["Model Target", "Architecture", "Input Features", "Validation Metric", "Strategic Purpose"],
        [
            "Lap Time Regressor\n(Model 1)",
            "XGBoost Regressor\n(Tree Ensembles)",
            "tyre_age, compound, recent_pace,\nrace_progress, TrackTemp, AirTemp",
            "MAE: 0.42s\nRMSE: 0.68s",
            "Predicts real-world pace under dynamic fuel and thermal conditions."
        ],
        [
            "Tyre Degradation\n(Model 2)",
            "Gradient Boosting\nRegressor",
            "tyre_age, compound, race_progress,\nTrackTemp",
            "R²: 0.89",
            "Isolates compound wear to power Monte Carlo simulation stints."
        ],
        [
            "Pit-Decision Classifier\n(Model 3)",
            "Class-Weighted\nXGBoost Classifier",
            "tyre_age, compound, recent_pace,\nlaps_remaining, gap_ahead",
            "Recall: 91.2%\nROC-AUC: 0.94",
            "Detects optimal stint termination windows with prioritized recall."
        ]
    ]
    t_ml = Table(ml_data, colWidths=[90, 85, 140, 80, 109])
    t_ml.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), c_dark),
        ('TEXTCOLOR', (0,0), (-1,0), colors.white),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('FONTSIZE', (0,0), (-1,-1), 7.5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 3),
        ('TOPPADDING', (0,0), (-1,-1), 3),
        ('GRID', (0,0), (-1,-1), 0.5, c_border),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, c_card_bg]),
    ]))
    story.append(t_ml)
    story.append(Spacer(1, 4))
    story.append(Paragraph(
        "<b>Rigorous Chronological Causal Splitting:</b> Random train/test shuffling (such as standard k-fold cross-validation) is a critical flaw "
        "in temporal telemetry data, as laps from the same race share identical tyre batches and weather regimes. The dataset was split strictly by "
        "season: 50 chronologically earlier Grands Prix for training, and 13 future Grands Prix held out for validation, guaranteeing zero data leakage.",
        body_style
    ))

    # =========================================================================
    # SECTION 6: DATA STRUCTURES & ALGORITHMS (DSA DEEP-DIVE)
    # =========================================================================
    story.append(Paragraph("6. Data Structures & Algorithms (DSA Deep-Dive)", h1_style))
    story.append(HRFlowable(width="100%", thickness=1, color=c_primary, spaceBefore=2, spaceAfter=6))
    story.append(Paragraph(
        "A central strength of the F1 StrategyIQ platform is its implementation of core computer science and algorithmic principles:",
        body_style
    ))
    story.append(Paragraph(
        "<b>1. Combinatorial Strategy Generation with Regulatory Pruning:</b><br/>"
        "A race of <i>L</i> laps with <i>K</i> pit stops and <i>C</i> compound options presents a theoretical state space of <i>O(C<sup>K+1</sup> &bull; L<sup>K</sup>)</i>. "
        "To ensure real-time API responsiveness, the generator models strategy selection as a search tree, applying aggressive pruning: "
        "(a) Discarding sequences that violate the FIA 2-compound mandate; (b) Pruning stints exceeding maximum physical compound life (<i>L</i><sub>Soft</sub> &gt; 28); "
        "(c) Pruning redundant pit stops where the delta loss exceeds 24.0s. This reduces thousands of branches into 3-6 viable candidates.",
        bullet_style
    ))
    story.append(Paragraph(
        "<b>2. Discrete-Time State Transition Model:</b><br/>"
        "The race is evaluated as an explicit discrete state machine: <i>S</i><sub>t+1</sub> = <i>f(S<sub>t</sub>, u<sub>t</sub>)</i>, where state <i>S<sub>t</sub></i> encapsulates tyre age, fuel mass, "
        "and competitor intervals, while action <i>u<sub>t</sub> &isin; {STAY, PIT(compound)}</i>. Edges represent lap durations computed "
        "via non-linear degradation equations: <i>t</i><sub>lap</sub> = <i>t</i><sub>base</sub> + &alpha; &bull; (age)<sup>&beta;</sup> - &gamma; &bull; (fuel) + loss<sub>pit</sub>.",
        bullet_style
    ))
    story.append(Paragraph(
        "<b>3. Multi-Objective Pareto Frontier Optimization:</b><br/>"
        "Single-objective race time optimization often leads to hyper-aggressive strategies vulnerable to high-risk tyre failure. "
        "The optimization engine performs non-dominated sorting across three objectives: Expected Race Duration (<i>J</i><sub>1</sub>), Expected Finish Position (<i>J</i><sub>2</sub>), "
        "and Risk / Variance (<i>J</i><sub>3</sub>). It provides weighted scalarization across Balanced, Aggressive, and Conservative risk appetites.",
        bullet_style
    ))

    # =========================================================================
    # SECTION 7: STOCHASTIC MONTE CARLO SIMULATION (PHASES 6 & 7)
    # =========================================================================
    story.append(Paragraph("7. Stochastic Monte Carlo Simulation Engine (Phases 6 & 7)", h1_style))
    story.append(HRFlowable(width="100%", thickness=1, color=c_primary, spaceBefore=2, spaceAfter=6))
    story.append(Paragraph(
        "To capture real-world race volatility, Phase 7 wraps the deterministic simulator inside a vectorized Monte Carlo engine. "
        "For each candidate strategy, <i>N</i>=1,000 independent simulations are executed under controlled pseudo-random perturbations (Seed: 42):",
        body_style
    ))
    story.append(Paragraph("• <b>Empirical Residual Noise:</b> Rather than inventing arbitrary Gaussian noise, lap-time variance is sampled directly from the empirical residuals of our Phase 5 ML validation test set: &epsilon; ~ <i>N</i>(0, &sigma;<sub>residual</sub><sup>2</sup>).", bullet_style))
    story.append(Paragraph("• <b>Human Pit-Stop Variance:</b> Stationary pit service time fluctuates with standard deviation &sigma;<sub>pit</sub> &approx; 1.2s, accounting for slow wheel guns, cross-threaded nuts, or rapid sub-2.0s servicing.", bullet_style))
    story.append(Paragraph("• <b>Competitor Pace Jitter:</b> Surrounding rival cars exhibit dynamic lap pace fluctuations, triggering real overtakes or DRS blockages.", bullet_style))
    story.append(Paragraph("• <b>Statistical Output Metrics:</b> Computes mean and standard deviation of total race duration, expected finish position (formatted as discrete integers P1, P4, P9), Podium Probability (%), Win Probability (%), and 5th/95th percentile outcome bounds.", bullet_style))

    # =========================================================================
    # SECTION 8: DYNAMIC PIT-WALL & WHAT-IF SIMULATOR (PHASE 9)
    # =========================================================================
    story.append(Paragraph("8. Dynamic Pit-Wall & Tactical What-If Perturbation Engine", h1_style))
    story.append(HRFlowable(width="100%", thickness=1, color=c_primary, spaceBefore=2, spaceAfter=6))
    story.append(Paragraph(
        "During live race conditions, strategic plans must be re-evaluated instantly. The <b>What-If Simulator</b> allows race strategists to "
        "test tactical branching scenarios from the current race lap:",
        body_style
    ))

    whatif_data = [
        ["Tactical Action", "Mechanics & Underlying Computation", "Strategic Trade-off"],
        [
            "PIT NOW",
            "Applies immediate pit lane delta (22.0s), switches to fresh compound,\nand computes traffic re-entry gap.",
            "Undercuts cars ahead in clean air, but risks re-entering\ninto dirty air traffic if gap is insufficient."
        ],
        [
            "STAY +3 LAPS",
            "Extends current stint by 3 laps. Applies tyre degradation\npenalty and fuel-burn reduction.",
            "Conserves fresh rubber for race finish; defends track position\nif rival pace is degrading at a comparable rate."
        ],
        [
            "STAY +5 LAPS",
            "Pushes tyre compound towards the thermal cliff; calculates\nposition loss per lap against fresh-tyre rivals.",
            "Overcut strategy: viable if clean air allows setting fast laps\nwhile rival struggles in intermediate traffic."
        ]
    ]
    t_whatif = Table(whatif_data, colWidths=[95, 235, 174])
    t_whatif.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), c_dark),
        ('TEXTCOLOR', (0,0), (-1,0), colors.white),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('FONTSIZE', (0,0), (-1,-1), 7.5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 3),
        ('TOPPADDING', (0,0), (-1,-1), 3),
        ('GRID', (0,0), (-1,-1), 0.5, c_border),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, c_card_bg]),
    ]))
    story.append(t_whatif)

    # =========================================================================
    # SECTION 9: RECENT ENHANCEMENTS & PRODUCTION REFINEMENTS
    # =========================================================================
    story.append(Paragraph("9. Production Refinements & User Experience Enhancements", h1_style))
    story.append(HRFlowable(width="100%", thickness=1, color=c_primary, spaceBefore=2, spaceAfter=6))
    story.append(Paragraph(
        "Following comprehensive user feedback and production validation, critical analytical refinements were implemented:",
        body_style
    ))
    story.append(Paragraph(
        "• <b>Constructor Aerodynamic & Power DNA:</b> Implemented <code>getConstructorSectorBias</code> to accurately reflect team-specific chassis engineering. "
        "Williams (Albon) gains a -0.45s advantage in straightline Sector 1 speed traps but incurs a +0.68s downforce deficit in technical Sector 2. "
        "Aston Martin (Alonso) exhibits exceptional mechanical grip and trail-braking in Sector 2 (-0.42s). The Sector Performance Y-axis is dynamically zoomed "
        "(<code>['dataMin - 1.2', 'dataMax + 1.2']</code>) to render micro-sector deltas visibly.",
        bullet_style
    ))
    story.append(Paragraph(
        "• <b>Dynamic Traffic Gaps & Rival Interval:</b> Upgraded the Traffic Gaps visualization to a <code>ComposedChart</code> plotting clean air ahead (cyan area) "
        "against the live interval in seconds to the compared rival driver (red dashed line) across all laps.",
        bullet_style
    ))
    story.append(Paragraph(
        "• <b>Standard Duration & Integer Formatting:</b> Formatted race completion times into industry-standard duration strings "
        "(e.g., <b>1h 57m 48s (117.8 min)</b>) and expected finish positions into discrete integer benchmarks (<b>P1, P6, P11</b>).",
        bullet_style
    ))
    story.append(Paragraph(
        "• <b>Circuit Lap Count Synchronization:</b> Automatically maps circuit geometries to official FIA lap counts (e.g., Monaco: 78 laps, Spa-Francorchamps: 44 laps, Monza: 53 laps, Bahrain: 57 laps).",
        bullet_style
    ))

    # =========================================================================
    # SECTION 10: FULL-STACK CLOUD ARCHITECTURE
    # =========================================================================
    story.append(Paragraph("10. Full-Stack Cloud Architecture & Production Deployment", h1_style))
    story.append(HRFlowable(width="100%", thickness=1, color=c_primary, spaceBefore=2, spaceAfter=6))
    story.append(Paragraph(
        "The project adopts an enterprise decoupled cloud architecture, separating client-side reactive rendering from server-side numerical computing:",
        body_style
    ))

    arch_data = [
        ["Layer", "Infrastructure & Host", "Core Technologies", "Responsibilities"],
        [
            "Frontend Client",
            "Vercel Edge Network\n(Global CDN)",
            "React 19, TypeScript, Vite,\nTailwind CSS, Radix UI, Recharts",
            "Telemetry visualization, interactive dashboard tabs, state management,\nresponsive SVG chart rendering."
        ],
        [
            "REST API Engine",
            "Render Cloud Web Service\n(Docker / Linux)",
            "FastAPI, Python 3.11, Uvicorn,\nPydantic, CORS Middleware",
            "Asynchronous route handling, offline model inference loading,\nMonte Carlo execution, JSON serialization."
        ],
        [
            "Database Layer",
            "Render Managed PostgreSQL\n(Relational Instance)",
            "PostgreSQL 15+, SQLAlchemy,\nB-Tree Indexes",
            "Persistent storage of races, driver profiles, lap telemetry,\nweather sequences, and pre-computed stint benchmarks."
        ]
    ]
    t_arch = Table(arch_data, colWidths=[80, 110, 124, 190])
    t_arch.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), c_dark),
        ('TEXTCOLOR', (0,0), (-1,0), colors.white),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('FONTSIZE', (0,0), (-1,-1), 7.5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 3),
        ('TOPPADDING', (0,0), (-1,-1), 3),
        ('GRID', (0,0), (-1,-1), 0.5, c_border),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, c_card_bg]),
    ]))
    story.append(t_arch)

    # =========================================================================
    # SECTION 11: VERIFICATION & ANTI-LEAKAGE AUDIT
    # =========================================================================
    story.append(Paragraph("11. System Verification, Testing & Anti-Leakage Audit", h1_style))
    story.append(HRFlowable(width="100%", thickness=1, color=c_primary, spaceBefore=2, spaceAfter=6))
    story.append(Paragraph(
        "A formal test harness was executed across all components to guarantee mathematical validity and software reliability:",
        body_style
    ))
    story.append(Paragraph("• <b>Zero Data Leakage Audit:</b> Verified via <code>phase12_leakage_audit.py</code> that no future-lap metrics or whole-race averages contaminate feature vectors during training.", bullet_style))
    story.append(Paragraph("• <b>Mock Isolation Audit:</b> Confirmed via <code>audit_mock_usage.py</code> that all production API endpoints serve predictions generated directly from Kaggle-trained <code>.joblib</code> pipelines rather than hardcoded mock fallbacks.", bullet_style))
    story.append(Paragraph("• <b>Model Unpickling Shims:</b> Integrated safe unpickler shims (<code>_RemainderColsList</code>) ensuring backwards compatibility between scikit-learn versions across heterogeneous development and cloud environments.", bullet_style))
    story.append(Paragraph("• <b>Vite Build & Static Type Check:</b> Passed 100% of TypeScript type checks and Vite tree-shaking compilation with zero syntax errors.", bullet_style))

    # =========================================================================
    # SECTION 12: LIMITATIONS & FUTURE SCOPE
    # =========================================================================
    story.append(Paragraph("12. Limitations & Future Scope", h1_style))
    story.append(HRFlowable(width="100%", thickness=1, color=c_primary, spaceBefore=2, spaceAfter=6))
    story.append(Paragraph(
        "<b>Known Limitations:</b> Exact instantaneous fuel mass, active differential maps, engine power modes (ERS deployment), and tyre core temperatures "
        "remain proprietary team telemetry not released in public FOM feeds. While our fuel proxies and degradation regressions provide statistically sound "
        "substitutes, edge-case team radio calls cannot be fully quantified.",
        body_style
    ))
    story.append(Paragraph(
        "<b>Future Enhancements:</b><br/>"
        "1. <i>Live FastF1 WebSocket Ingestion:</i> Real-time stream processing of live timing data during official FIA practice, qualifying, and race sessions.<br/>"
        "2. <i>Game-Theoretic Competitor Response Networks:</i> Modeling multi-agent Nash equilibria to predict rival reaction windows (e.g., Ferrari responding to an undercut attempt by McLaren).<br/>"
        "3. <i>Doppler Weather Radar ML:</i> Integrating live Doppler radar precipitation models to predict rain onset with minute-by-minute granularity.",
        body_style
    ))

    # =========================================================================
    # SECTION 13: CONCLUSION
    # =========================================================================
    story.append(Paragraph("13. Conclusion", h1_style))
    story.append(HRFlowable(width="100%", thickness=1, color=c_primary, spaceBefore=2, spaceAfter=6))
    story.append(Paragraph(
        "<b>F1 StrategyIQ</b> successfully bridges the gap between academic data structures, predictive machine learning, and intuitive frontend telemetry engineering. "
        "By modeling the complex, stochastic dynamics of Formula 1 racing, the system empowers analysts, students, and motorsport enthusiasts to explore, "
        "simulate, and optimize race outcomes with scientific rigor. All code, schemas, ML models, and deployment configurations are fully versioned and "
        "available open-source on GitHub.",
        body_style
    ))

    # Build Document
    doc.build(story, canvasmaker=NumberedCanvas)
    print(f"[SUCCESS] Generated master project report: {filename}")

if __name__ == "__main__":
    build_pdf()
