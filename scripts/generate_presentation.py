import os
import sys
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.enum.shapes import MSO_SHAPE

def create_deck(output_path="F1_StrategyIQ_Final_Presentation.pptx"):
    prs = Presentation()
    # 16:9 Widescreen layout
    prs.slide_width = Inches(13.333)
    prs.slide_height = Inches(7.5)

    blank_layout = prs.slide_layouts[6]

    # Theme Colors
    BG_COLOR = RGBColor(15, 23, 42)        # Slate 900 #0F172A
    CARD_BG = RGBColor(30, 41, 59)        # Slate 800 #1E293B
    CARD_BORDER = RGBColor(51, 65, 85)    # Slate 700 #334155
    RED = RGBColor(225, 6, 0)             # F1 Racing Red #E10600
    WHITE = RGBColor(248, 250, 252)       # Slate 50 #F8FAFC
    MUTED = RGBColor(148, 163, 184)       # Slate 400 #94A3B8
    CYAN = RGBColor(14, 165, 233)         # Sky 500 #0EA5E9
    LIME = RGBColor(16, 185, 129)         # Emerald 500 #10B981
    AMBER = RGBColor(245, 158, 11)        # Amber 500 #F59E0B

    def set_slide_background(slide):
        bg = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, Inches(13.333), Inches(7.5))
        bg.fill.solid()
        bg.fill.fore_color.rgb = BG_COLOR
        bg.line.fill.background()
        return bg

    def add_header(slide, tag_text, title_text):
        # Category Tag
        tag_box = slide.shapes.add_textbox(Inches(0.8), Inches(0.4), Inches(11.5), Inches(0.35))
        tf_tag = tag_box.text_frame
        tf_tag.word_wrap = True
        tf_tag.margin_left = tf_tag.margin_top = tf_tag.margin_right = tf_tag.margin_bottom = 0
        p_tag = tf_tag.paragraphs[0]
        p_tag.text = tag_text.upper()
        p_tag.font.size = Pt(10)
        p_tag.font.bold = True
        p_tag.font.color.rgb = RED

        # Title
        title_box = slide.shapes.add_textbox(Inches(0.8), Inches(0.72), Inches(11.5), Inches(0.65))
        tf_title = title_box.text_frame
        tf_title.word_wrap = True
        tf_title.margin_left = tf_title.margin_top = tf_title.margin_right = tf_title.margin_bottom = 0
        p_title = tf_title.paragraphs[0]
        p_title.text = title_text
        p_title.font.size = Pt(22)
        p_title.font.bold = True
        p_title.font.color.rgb = WHITE

        # Accent Line
        line = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0.8), Inches(1.4), Inches(2.2), Inches(0.04))
        line.fill.solid()
        line.fill.fore_color.rgb = RED
        line.line.fill.background()

        # Running Footer
        footer_box = slide.shapes.add_textbox(Inches(0.8), Inches(7.05), Inches(11.733), Inches(0.3))
        tf_f = footer_box.text_frame
        tf_f.margin_left = tf_f.margin_top = tf_f.margin_right = tf_f.margin_bottom = 0
        p_f = tf_f.paragraphs[0]
        p_f.text = "F1 StrategyIQ • Formula 1 Race Strategy Optimization Platform • DSA & Machine Learning Project"
        p_f.font.size = Pt(8.5)
        p_f.font.color.rgb = MUTED

    def add_card(slide, left, top, width, height, title=None, border_color=CARD_BORDER):
        card = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(left), Inches(top), Inches(width), Inches(height))
        card.fill.solid()
        card.fill.fore_color.rgb = CARD_BG
        card.line.color.rgb = border_color
        card.line.width = Pt(1)

        if title:
            tb = slide.shapes.add_textbox(Inches(left + 0.25), Inches(top + 0.2), Inches(width - 0.5), Inches(0.4))
            tf = tb.text_frame
            tf.word_wrap = True
            tf.margin_left = tf.margin_top = tf.margin_right = tf.margin_bottom = 0
            p = tf.paragraphs[0]
            p.text = title
            p.font.size = Pt(13)
            p.font.bold = True
            p.font.color.rgb = WHITE
        return card

    # =========================================================================
    # SLIDE 1: TITLE SLIDE (COVER)
    # =========================================================================
    s1 = prs.slides.add_slide(blank_layout)
    set_slide_background(s1)

    # Decorative top bar
    bar = s1.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, Inches(13.333), Inches(0.12))
    bar.fill.solid()
    bar.fill.fore_color.rgb = RED
    bar.line.fill.background()

    # Brand badge
    badge = s1.shapes.add_textbox(Inches(1.0), Inches(1.3), Inches(10), Inches(0.4))
    p = badge.text_frame.paragraphs[0]
    p.text = "FORMULA 1 • STRATEGIC INTELLIGENCE PLATFORM"
    p.font.size = Pt(12)
    p.font.bold = True
    p.font.color.rgb = RED

    # Main Title
    tbox = s1.shapes.add_textbox(Inches(1.0), Inches(1.8), Inches(11.3), Inches(1.8))
    tf = tbox.text_frame
    tf.word_wrap = True
    p1 = tf.paragraphs[0]
    p1.text = "F1 StrategyIQ: Data-Driven Race Strategy Optimization & Dynamic Pit-Wall System"
    p1.font.size = Pt(32)
    p1.font.bold = True
    p1.font.color.rgb = WHITE

    # Subtitle
    sbox = s1.shapes.add_textbox(Inches(1.0), Inches(3.6), Inches(11.0), Inches(0.8))
    p2 = sbox.text_frame.paragraphs[0]
    p2.text = "Bridging Data Structures & Algorithms, Causal Machine Learning Telemetry, and Stochastic Monte Carlo Simulations for Real-Time Race Decision Support"
    p2.font.size = Pt(14)
    p2.font.color.rgb = MUTED

    # Metadata Card
    add_card(s1, 1.0, 4.6, 11.333, 1.9, None)
    mbox = s1.shapes.add_textbox(Inches(1.3), Inches(4.8), Inches(10.7), Inches(1.5))
    mtf = mbox.text_frame
    mtf.word_wrap = True
    
    mp1 = mtf.paragraphs[0]
    mp1.text = "PROJECT DOMAIN: Data Structures & Algorithms (DSA) • Applied Machine Learning • Full-Stack Distributed Systems"
    mp1.font.size = Pt(11)
    mp1.font.bold = True
    mp1.font.color.rgb = CYAN

    mp2 = mtf.add_paragraph()
    mp2.text = "TECH STACK: Python 3.11 • FastAPI • React 19 • TypeScript • PostgreSQL • XGBoost • Scikit-Learn • Vite • Tailwind CSS"
    mp2.font.size = Pt(10)
    mp2.font.color.rgb = WHITE

    mp3 = mtf.add_paragraph()
    mp3.text = "DEPLOYMENTS: Frontend on Vercel • Backend & Managed PostgreSQL on Render Cloud"
    mp3.font.size = Pt(10)
    mp3.font.color.rgb = LIME

    mp4 = mtf.add_paragraph()
    mp4.text = "REPOSITORIES: github.com/sanskar620/DSA_F1  |  github.com/sanskar620/strategyiq  |  Release v2.0"
    mp4.font.size = Pt(9.5)
    mp4.font.color.rgb = MUTED

    s1.notes_slide.notes_text_frame.text = (
        "Good morning/afternoon. Today I am presenting F1 StrategyIQ, an enterprise-grade tactical intelligence platform "
        "designed to optimize Formula 1 race strategies. The project integrates fundamental Data Structures and Algorithms with "
        "causal machine learning and Monte Carlo simulations, delivering a real-time full-stack decision-support platform."
    )

    # =========================================================================
    # SLIDE 2: PROBLEM STATEMENT & MOTIVATION
    # =========================================================================
    s2 = prs.slides.add_slide(blank_layout)
    set_slide_background(s2)
    add_header(s2, "Domain Challenges", "Problem Statement & Tactical Complexity")

    # Card 1: Split-Second Margins
    add_card(s2, 0.8, 1.7, 3.6, 5.0, "1. Split-Second Margins")
    tb = s2.shapes.add_textbox(Inches(1.05), Inches(2.3), Inches(3.1), Inches(4.2))
    tf = tb.text_frame
    tf.word_wrap = True
    bullets = [
        ("High Stakes:", " A 2-second error in pit timing drops a front-runner from P1 into a mid-field DRS train."),
        ("Pit Delta Loss:", " Pitting incurs a ~22.0s - 25.0s transit penalty that must be recouped via fresher tyre pace."),
        ("Dynamic Undercut:", " Competitors trigger aggressive undercuts; failing to respond within 1 lap results in permanent track position loss.")
    ]
    for b_title, b_text in bullets:
        p = tf.add_paragraph() if tf.paragraphs[0].text else tf.paragraphs[0]
        r1 = p.add_run()
        r1.text = "• " + b_title
        r1.font.bold = True
        r1.font.size = Pt(10.5)
        r1.font.color.rgb = WHITE
        r2 = p.add_run()
        r2.text = b_text
        r2.font.size = Pt(10)
        r2.font.color.rgb = MUTED

    # Card 2: Stochastic Non-Linearity
    add_card(s2, 4.86, 1.7, 3.6, 5.0, "2. Non-Linear Variables")
    tb = s2.shapes.add_textbox(Inches(5.11), Inches(2.3), Inches(3.1), Inches(4.2))
    tf = tb.text_frame
    tf.word_wrap = True
    bullets = [
        ("Tyre Degradation Cliffs:", " Rubber degradation is non-linear; compounds hit a thermal cliff where pace drops by >1.5s/lap."),
        ("Traffic Dirty Air:", " Trailing within 1.5s of a rival car induces aerodynamic turbulence, costing 0.8s - 1.4s per lap."),
        ("Pit Crew Jitter:", " Stationary pit service exhibits human latency variance (~1.2s standard deviation).")
    ]
    for b_title, b_text in bullets:
        p = tf.add_paragraph() if tf.paragraphs[0].text else tf.paragraphs[0]
        r1 = p.add_run()
        r1.text = "• " + b_title
        r1.font.bold = True
        r1.font.size = Pt(10.5)
        r1.font.color.rgb = WHITE
        r2 = p.add_run()
        r2.text = b_text
        r2.font.size = Pt(10)
        r2.font.color.rgb = MUTED

    # Card 3: The Algorithmic Solution
    add_card(s2, 8.93, 1.7, 3.6, 5.0, "3. F1 StrategyIQ Solution")
    tb = s2.shapes.add_textbox(Inches(9.18), Inches(2.3), Inches(3.1), Inches(4.2))
    tf = tb.text_frame
    tf.word_wrap = True
    bullets = [
        ("Tree Search & Pruning:", " Pruning candidate strategy combinations down to viable regulations-compliant paths."),
        ("Stochastic Monte Carlo:", " 1,000 simulations sampling empirical telemetry residuals for risk quantification."),
        ("Pareto Multi-Objective:", " Finding optimal trade-offs between minimum race time, best position, and risk tolerance.")
    ]
    for b_title, b_text in bullets:
        p = tf.add_paragraph() if tf.paragraphs[0].text else tf.paragraphs[0]
        r1 = p.add_run()
        r1.text = "• " + b_title
        r1.font.bold = True
        r1.font.size = Pt(10.5)
        r1.font.color.rgb = WHITE
        r2 = p.add_run()
        r2.text = b_text
        r2.font.size = Pt(10)
        r2.font.color.rgb = MUTED

    s2.notes_slide.notes_text_frame.text = (
        "In Formula 1, deterministic calculations fail because racing is intrinsically stochastic. "
        "A strategy that appears fast on paper can be completely derailed by traffic or pit stop variance. "
        "We frame this as a multi-objective optimization problem under severe non-linear constraints."
    )

    # =========================================================================
    # SLIDE 3: SYSTEM ARCHITECTURE & FULL-STACK PIPELINE
    # =========================================================================
    s3 = prs.slides.add_slide(blank_layout)
    set_slide_background(s3)
    add_header(s3, "System Engineering", "Full-Stack Distributed System Architecture")

    # 3 Layer Cards
    # Left: Frontend
    add_card(s3, 0.8, 1.7, 3.6, 5.0, "Frontend Layer (Vercel)")
    tb = s3.shapes.add_textbox(Inches(1.05), Inches(2.3), Inches(3.1), Inches(4.2))
    tf = tb.text_frame
    tf.word_wrap = True
    f_bullets = [
        "React 19 & TypeScript for type-safe interactive components",
        "Vite build tool with sub-4s tree-shaking compilation",
        "Tailwind CSS & Radix UI accessible dark-mode UI design",
        "Recharts SVG data visualization: LineCharts, ComposedCharts, BarCharts",
        "Global edge delivery via Vercel Edge Network"
    ]
    for b in f_bullets:
        p = tf.add_paragraph() if tf.paragraphs[0].text else tf.paragraphs[0]
        p.text = "• " + b
        p.font.size = Pt(10)
        p.font.color.rgb = MUTED

    # Middle: Backend
    add_card(s3, 4.86, 1.7, 3.6, 5.0, "Backend REST Engine (Render)")
    tb = s3.shapes.add_textbox(Inches(5.11), Inches(2.3), Inches(3.1), Inches(4.2))
    tf = tb.text_frame
    tf.word_wrap = True
    b_bullets = [
        "FastAPI high-throughput asynchronous REST server (Python 3.11)",
        "Uvicorn ASGI production server handling concurrent requests",
        "Offline ML model inference pipeline using Joblib",
        "Vectorized NumPy Monte Carlo calculation routines (<100ms latency)",
        "CORS middleware & continuous health monitoring at /api/health"
    ]
    for b in b_bullets:
        p = tf.add_paragraph() if tf.paragraphs[0].text else tf.paragraphs[0]
        p.text = "• " + b
        p.font.size = Pt(10)
        p.font.color.rgb = MUTED

    # Right: Data & ML
    add_card(s3, 8.93, 1.7, 3.6, 5.0, "Data & Modeling Layer")
    tb = s3.shapes.add_textbox(Inches(9.18), Inches(2.3), Inches(3.1), Inches(4.2))
    tf = tb.text_frame
    tf.word_wrap = True
    d_bullets = [
        "Managed PostgreSQL 15+ database hosted on Render",
        "Relational tables: races, drivers, results, laps, pit_stops, weather",
        "Pre-computed empirical residual distributions from 67,204 laps",
        "XGBoost Classifier & Regressors serialized as .joblib pipelines",
        "Unpickling compatibility shims ensuring cloud runtime safety"
    ]
    for b in d_bullets:
        p = tf.add_paragraph() if tf.paragraphs[0].text else tf.paragraphs[0]
        p.text = "• " + b
        p.font.size = Pt(10)
        p.font.color.rgb = MUTED

    s3.notes_slide.notes_text_frame.text = (
        "Our architecture decouples compute-heavy ML simulation from real-time client rendering. "
        "The frontend is deployed globally on Vercel's edge network, while FastAPI and PostgreSQL run on Render. "
        "Communication occurs via asynchronous REST endpoints with full CORS and schema validation."
    )

    # =========================================================================
    # SLIDE 4: CORE DATA STRUCTURES & ALGORITHMS (DSA DEEP-DIVE)
    # =========================================================================
    s4 = prs.slides.add_slide(blank_layout)
    set_slide_background(s4)
    add_header(s4, "Algorithmic Core", "Data Structures & Algorithms (DSA Deep-Dive)")

    # Left: Strategy Tree Search & Pruning
    add_card(s4, 0.8, 1.7, 5.65, 5.0, "1. Strategy Search Tree & Regulatory Pruning")
    tb = s4.shapes.add_textbox(Inches(1.05), Inches(2.3), Inches(5.15), Inches(4.2))
    tf = tb.text_frame
    tf.word_wrap = True
    items = [
        ("Combinatorial Complexity:", " A race of L laps with K stops and C tyre choices yields O(C^(K+1) * L^K) states. A brute-force search over 60 laps exceeds millions of permutations."),
        ("Branch Pruning Rule 1 (FIA Mandate):", " Discard any path where all stints use the same dry tyre compound (must use >= 2 distinct compounds)."),
        ("Branch Pruning Rule 2 (Tyre Mileage Limit):", " Discard branches exceeding empirical maximum tyre life (e.g. Soft > 28 laps)."),
        ("Branch Pruning Rule 3 (Pit Loss Dominance):", " Prune redundant pit stops where cumulative 24.0s pit transit loss cannot be recouped over remaining race distance."),
        ("Algorithmic Result:", " Reduces the search space to 3-6 highly competitive Pareto candidate strategies in sub-10 milliseconds.")
    ]
    for b_title, b_text in items:
        p = tf.add_paragraph() if tf.paragraphs[0].text else tf.paragraphs[0]
        r1 = p.add_run()
        r1.text = "• " + b_title
        r1.font.bold = True
        r1.font.size = Pt(9.5)
        r1.font.color.rgb = WHITE
        r2 = p.add_run()
        r2.text = b_text
        r2.font.size = Pt(9)
        r2.font.color.rgb = MUTED

    # Right: State Machine & Pareto Frontier
    add_card(s4, 6.85, 1.7, 5.65, 5.0, "2. State Transition Model & Pareto Optimization")
    tb = s4.shapes.add_textbox(Inches(7.1), Inches(2.3), Inches(5.15), Inches(4.2))
    tf = tb.text_frame
    tf.word_wrap = True
    items = [
        ("Discrete-Time State Machine:", " S(t+1) = f(S(t), u(t)), where state S(t) = <Lap, Compound, TyreAge, FuelMass, CompetitorGaps> and action u(t) in {STAY, PIT(compound)}."),
        ("Dynamic Edge Weights:", " Lap time weights computed by: t_lap = t_base + alpha * (TyreAge)^beta - gamma * (FuelMass) + PitDelta."),
        ("Pareto Multi-Objective Optimization:", " Solves a vector minimization problem: min [ J1(Time), J2(Position), J3(Risk) ]."),
        ("Scalarization Profiles:", " Balanced (equal weight on time and position), Aggressive (maximizing P1/Podium probability), and Conservative (minimizing risk variance)."),
        ("Complexity Guarantee:", " All candidates evaluated simultaneously using vectorized matrix operations in O(N * L) time.")
    ]
    for b_title, b_text in items:
        p = tf.add_paragraph() if tf.paragraphs[0].text else tf.paragraphs[0]
        r1 = p.add_run()
        r1.text = "• " + b_title
        r1.font.bold = True
        r1.font.size = Pt(9.5)
        r1.font.color.rgb = WHITE
        r2 = p.add_run()
        r2.text = b_text
        r2.font.size = Pt(9)
        r2.font.color.rgb = MUTED

    s4.notes_slide.notes_text_frame.text = (
        "Here is the core DSA contribution: We do not brute force every combination. "
        "We construct a decision tree pruned by FIA sporting regulations and tyre physical limits. "
        "The race is evaluated as a discrete state transition graph, and candidates are ranked along a Pareto optimal frontier."
    )

    # =========================================================================
    # SLIDE 5: MACHINE LEARNING PIPELINE (PHASE 5)
    # =========================================================================
    s5 = prs.slides.add_slide(blank_layout)
    set_slide_background(s5)
    add_header(s5, "Predictive Telemetry", "Machine Learning Telemetry Engine (Phase 5)")

    # Left Card: ML Architecture
    add_card(s5, 0.8, 1.7, 6.0, 5.0, "Supervised Telemetry Models")
    tb = s5.shapes.add_textbox(Inches(1.05), Inches(2.3), Inches(5.5), Inches(4.2))
    tf = tb.text_frame
    tf.word_wrap = True
    ml_pts = [
        ("Dataset Scale:", " 67,204 validated historical laps across 63 Formula 1 Grands Prix."),
        ("Chronological Causal Split:", " Random k-fold cross-validation was strictly prohibited to prevent data leakage. Split chronologically: 50 train races, 13 holdout evaluation races."),
        ("Model 1 - Lap-Time Regressor (XGBoost):", " Features: tyre_age, compound, recent_pace, race_progress, TrackTemp, AirTemp. Achieved validation MAE = 0.42s, RMSE = 0.68s."),
        ("Model 2 - Tyre Performance Regressor:", " Isolates compound degradation curves (R² = 0.89) to feed simulation stints."),
        ("Model 3 - Pit-Decision Classifier:", " Class-weighted gradient booster. Pits account for only ~2% of laps; recall was prioritized (91.2% Recall, ROC-AUC 0.94).")
    ]
    for b_title, b_text in ml_pts:
        p = tf.add_paragraph() if tf.paragraphs[0].text else tf.paragraphs[0]
        r1 = p.add_run()
        r1.text = "• " + b_title
        r1.font.bold = True
        r1.font.size = Pt(9.5)
        r1.font.color.rgb = WHITE
        r2 = p.add_run()
        r2.text = b_text
        r2.font.size = Pt(9)
        r2.font.color.rgb = MUTED

    # Right Card: Tyre Degradation Graph
    add_card(s5, 7.2, 1.7, 5.333, 5.0, "Empirical Tyre Degradation Curves")
    img_path = os.path.join("analysis", "figures", "tyre_degradation_curve.png")
    if os.path.exists(img_path):
        s5.shapes.add_picture(img_path, Inches(7.45), Inches(2.4), width=Inches(4.833))
    
    cap_box = s5.shapes.add_textbox(Inches(7.45), Inches(5.9), Inches(4.833), Inches(0.6))
    cp = cap_box.text_frame.paragraphs[0]
    cp.text = "Empirical pace degradation per compound (Soft, Medium, Hard) isolating thermal wear across stint age."
    cp.font.size = Pt(8.5)
    cp.font.color.rgb = MUTED

    s5.notes_slide.notes_text_frame.text = (
        "Phase 5 trained 3 supervised models on 67,000+ laps. "
        "Notice the critical methodology: we used a chronological split across full seasons rather than random shuffling, "
        "guaranteeing zero future-lap data leakage. The pit classifier achieved 91.2% recall despite extreme class imbalance."
    )

    # =========================================================================
    # SLIDE 6: STOCHASTIC MONTE CARLO SIMULATION
    # =========================================================================
    s6 = prs.slides.add_slide(blank_layout)
    set_slide_background(s6)
    add_header(s6, "Stochastic Modeling", "Monte Carlo Simulation Engine (Phases 6 & 7)")

    add_card(s6, 0.8, 1.7, 5.65, 5.0, "Stochastic Injection Methodology")
    tb = s6.shapes.add_textbox(Inches(1.05), Inches(2.3), Inches(5.15), Inches(4.2))
    tf = tb.text_frame
    tf.word_wrap = True
    mc_pts = [
        ("N = 1,000 Iterations:", " Evaluates each candidate strategy across 1,000 independent stochastic runs under fixed random seed (Seed: 42) for scientific reproducibility."),
        ("Empirical Lap-Time Noise:", " Rather than arbitrary Gaussian noise, residuals are sampled directly from actual Phase 5 test predictions: e ~ N(0, sigma_residual^2)."),
        ("Pit-Stop Execution Variance:", " Pit lane loss varies with standard deviation sigma = 1.2s, modeling wheel-gun snags and lightning-fast 2.0s stops."),
        ("Competitor Pace Turbulence:", " Competitor paces fluctuate organically across laps, generating real overtakes, DRS trains, and traffic blockages."),
        ("Tyre Degradation Consistency:", " Avoids double-counting: tyre degradation is already captured in the baseline ML regressor.")
    ]
    for b_title, b_text in mc_pts:
        p = tf.add_paragraph() if tf.paragraphs[0].text else tf.paragraphs[0]
        r1 = p.add_run()
        r1.text = "• " + b_title
        r1.font.bold = True
        r1.font.size = Pt(9.5)
        r1.font.color.rgb = WHITE
        r2 = p.add_run()
        r2.text = b_text
        r2.font.size = Pt(9)
        r2.font.color.rgb = MUTED

    add_card(s6, 6.85, 1.7, 5.65, 5.0, "Statistical Output Distributions")
    tb = s6.shapes.add_textbox(Inches(7.1), Inches(2.3), Inches(5.15), Inches(4.2))
    tf = tb.text_frame
    tf.word_wrap = True
    out_pts = [
        ("Expected Race Duration:", " Mean and median total time, with 5th and 95th confidence percentile intervals."),
        ("Integer Expected Finish:", " Discrete finish ranking (P1, P4, P9) rather than misleading floating-point decimals."),
        ("Podium & Win Probabilities:", " Percentage of the 1,000 simulated iterations where the car finishes in P1 or the top 3."),
        ("Risk Metric (Standard Deviation):", " Spread of race outcomes used as the primary indicator for tactical risk."),
        ("Strategy Recommendation:", " Ranks candidate strategies (e.g. M-S vs M-H vs M-M-H) by Pareto scalarization score.")
    ]
    for b_title, b_text in out_pts:
        p = tf.add_paragraph() if tf.paragraphs[0].text else tf.paragraphs[0]
        r1 = p.add_run()
        r1.text = "• " + b_title
        r1.font.bold = True
        r1.font.size = Pt(9.5)
        r1.font.color.rgb = WHITE
        r2 = p.add_run()
        r2.text = b_text
        r2.font.size = Pt(9)
        r2.font.color.rgb = MUTED

    s6.notes_slide.notes_text_frame.text = (
        "Phase 7 turns deterministic models into probability distributions. "
        "By simulating 1,000 runs with empirical telemetry residuals, we output real win probabilities and risk variances. "
        "This allows teams to pick strategies aligned with their specific championship risk appetite."
    )

    # =========================================================================
    # SLIDE 7: STRATEGY OPTIMIZER & STANDARD UNITS
    # =========================================================================
    s7 = prs.slides.add_slide(blank_layout)
    set_slide_background(s7)
    add_header(s7, "Strategic Optimization", "Multi-Objective Strategy Optimizer & Metrics")

    # Table Card
    add_card(s7, 0.8, 1.7, 11.733, 5.0, "Ranked Candidate Strategy Evaluation (Bahrain GP Sample)")
    
    # Insert Table
    rows = 6
    cols = 6
    table_shape = s7.shapes.add_table(rows, cols, Inches(1.1), Inches(2.3), Inches(11.133), Inches(2.6))
    table = table_shape.table
    table.columns[0].width = Inches(2.4)
    table.columns[1].width = Inches(2.8)
    table.columns[2].width = Inches(1.6)
    table.columns[3].width = Inches(1.4)
    table.columns[4].width = Inches(1.4)
    table.columns[5].width = Inches(1.533)

    headers = ["Strategy", "Expected Time (Duration)", "Expected Finish", "Podium %", "Win %", "Risk Level"]
    for i, h in enumerate(headers):
        cell = table.cell(0, i)
        cell.text = h
        cell.fill.solid()
        cell.fill.fore_color.rgb = RED
        for p in cell.text_frame.paragraphs:
            p.font.size = Pt(10)
            p.font.bold = True
            p.font.color.rgb = WHITE

    sample_data = [
        ["M - S  [RECOMMENDED]", "1h 57m 48s (117.8 min)", "P1", "100%", "100%", "High (Fastest)"],
        ["M - H", "1h 57m 46s (117.8 min)", "P1", "100%", "100%", "High"],
        ["M - M - H", "1h 59m 04s (119.1 min)", "P6", "0%", "0%", "High"],
        ["M - H - M", "1h 59m 08s (119.1 min)", "P6", "0%", "0%", "High"],
        ["M - H - S", "1h 59m 47s (119.8 min)", "P11", "0%", "0%", "High"]
    ]
    for row_idx, row in enumerate(sample_data):
        for col_idx, val in enumerate(row):
            cell = table.cell(row_idx + 1, col_idx)
            cell.text = val
            cell.fill.solid()
            cell.fill.fore_color.rgb = CARD_BG
            for p in cell.text_frame.paragraphs:
                p.font.size = Pt(9.5)
                p.font.color.rgb = LIME if col_idx == 0 and "RECOMMENDED" in val else WHITE

    # Callout notes below table
    n_box = s7.shapes.add_textbox(Inches(1.1), Inches(5.1), Inches(11.133), Inches(1.3))
    tf = n_box.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text = "KEY METRIC REFINEMENTS IMPLEMENTED:"
    p.font.size = Pt(10.5)
    p.font.bold = True
    p.font.color.rgb = CYAN

    pts = [
        "Standard Duration Units: Converted raw simulation seconds into human-readable hours, minutes, and seconds (e.g. 1h 57m 48s).",
        "Integer Finish Positions: Formatted expected finish positions as whole rankings (P1, P6, P11) for tactical clarity.",
        "Sensitivity Profiling: Validated strategy robustness across Balanced, Aggressive, and Risk-Aware objective weighting."
    ]
    for pt in pts:
        p = tf.add_paragraph()
        p.text = "• " + pt
        p.font.size = Pt(9.5)
        p.font.color.rgb = MUTED

    s7.notes_slide.notes_text_frame.text = (
        "Here is the Strategy Optimizer in action. Notice how we format expected times into human-readable duration strings "
        "and integer finish rankings. The M-S and M-H one-stop strategies clearly dominate the three-stop configurations by over 1.3 minutes."
    )

    # =========================================================================
    # SLIDE 8: COMPARATIVE RACE DIAGNOSTICS & CONSTRUCTOR DNA
    # =========================================================================
    s8 = prs.slides.add_slide(blank_layout)
    set_slide_background(s8)
    add_header(s8, "Telemetry Diagnostics", "Head-to-Head Race Analysis & Constructor DNA")

    add_card(s8, 0.8, 1.7, 5.65, 5.0, "Constructor Aerodynamic & Power DNA")
    tb = s8.shapes.add_textbox(Inches(1.05), Inches(2.3), Inches(5.15), Inches(4.2))
    tf = tb.text_frame
    tf.word_wrap = True
    c_pts = [
        ("Constructor Sector Bias:", " Real F1 cars have unique DNA. Williams is fast in a straight line; Aston Martin excels in mechanical braking."),
        ("Williams / Albon Profile:", " Low-drag aero gives a -0.45s advantage in straightline Sector 1 speed traps, but incurs a +0.68s downforce penalty in technical Sector 2."),
        ("Aston Martin / Alonso Profile:", " High mechanical downforce grants a -0.42s advantage in Sector 2 trail-braking, with slightly higher drag in Sector 1 (+0.32s)."),
        ("Zoomed Sector Y-Axis:", " Set Y-axis domain to ['dataMin - 1.2', 'dataMax + 1.2'], making micro-sector deltas (0.2s - 0.7s) visually distinct and readable."),
        ("Circuit Lap Counts:", " Mapped to official circuit lengths (Monaco: 78, Spa: 44, Monza: 53, Bahrain: 57).")
    ]
    for b_title, b_text in c_pts:
        p = tf.add_paragraph() if tf.paragraphs[0].text else tf.paragraphs[0]
        r1 = p.add_run()
        r1.text = "• " + b_title
        r1.font.bold = True
        r1.font.size = Pt(9.5)
        r1.font.color.rgb = WHITE
        r2 = p.add_run()
        r2.text = b_text
        r2.font.size = Pt(9)
        r2.font.color.rgb = MUTED

    add_card(s8, 6.85, 1.7, 5.65, 5.0, "Traffic Gaps & Live Rival Interval")
    tb = s8.shapes.add_textbox(Inches(7.1), Inches(2.3), Inches(5.15), Inches(4.2))
    tf = tb.text_frame
    tf.word_wrap = True
    g_pts = [
        ("ComposedChart Upgrade:", " Replaced static charts with a dynamic ComposedChart displaying both clean air and rival delta."),
        ("Clean Air Ahead (Area):", " Cyan gradient represents gap to the car ahead based on grid position and overtaking difficulty."),
        ("Live Rival Delta (Dotted Line):", " Red dashed line tracks the live interval in seconds to the compared rival driver across all laps."),
        ("Pit Delta Disruption:", " Visualizes the sudden 22s gap drop during pit stops and the subsequent recovery on fresher tyres."),
        ("Teammate vs Rival Mode:", " Allows instant switching to compare telemetry against any driver on the 20-car grid.")
    ]
    for b_title, b_text in g_pts:
        p = tf.add_paragraph() if tf.paragraphs[0].text else tf.paragraphs[0]
        r1 = p.add_run()
        r1.text = "• " + b_title
        r1.font.bold = True
        r1.font.size = Pt(9.5)
        r1.font.color.rgb = WHITE
        r2 = p.add_run()
        r2.text = b_text
        r2.font.size = Pt(9)
        r2.font.color.rgb = MUTED

    s8.notes_slide.notes_text_frame.text = (
        "In our latest update, we implemented realistic constructor chassis biases. "
        "A Williams car shows realistic top speed advantages in Sector 1 speed traps, while Aston Martin dominates technical Sector 2 corners. "
        "The traffic gap chart dynamically tracks the interval to any selected rival."
    )

    # =========================================================================
    # SLIDE 9: DYNAMIC PIT-WALL & WHAT-IF SIMULATOR
    # =========================================================================
    s9 = prs.slides.add_slide(blank_layout)
    set_slide_background(s9)
    add_header(s9, "Tactical Decision Support", "Dynamic Pit-Wall & What-If Scenario Simulator")

    # 3 Scenario Cards
    # Card 1: Pit Now
    add_card(s9, 0.8, 1.7, 3.6, 5.0, "Tactical Fork: PIT NOW")
    tb = s9.shapes.add_textbox(Inches(1.05), Inches(2.3), Inches(3.1), Inches(4.2))
    tf = tb.text_frame
    tf.word_wrap = True
    p_pts = [
        ("Action:", " Immediate pit stop call on the current lap."),
        ("Expected Time:", " 89m 10s total duration."),
        ("Expected Finish:", " P9.8 (Drops into heavy mid-field traffic)."),
        ("Podium Probability:", " 0% (Clean air lost)."),
        ("Risk Level:", " HIGH."),
        ("Tactical Verdict:", " Premature pit stop sacrifices track position before tyre wear threshold is reached.")
    ]
    for b_title, b_text in p_pts:
        p = tf.add_paragraph() if tf.paragraphs[0].text else tf.paragraphs[0]
        r1 = p.add_run()
        r1.text = "• " + b_title
        r1.font.bold = True
        r1.font.size = Pt(9.5)
        r1.font.color.rgb = WHITE
        r2 = p.add_run()
        r2.text = b_text
        r2.font.size = Pt(9)
        r2.font.color.rgb = MUTED

    # Card 2: Stay 3 Laps
    add_card(s9, 4.86, 1.7, 3.6, 5.0, "Tactical Fork: STAY +3 LAPS")
    tb = s9.shapes.add_textbox(Inches(5.11), Inches(2.3), Inches(3.1), Inches(4.2))
    tf = tb.text_frame
    tf.word_wrap = True
    s3_pts = [
        ("Action:", " Extend current stint by exactly 3 laps."),
        ("Expected Time:", " 88m 47s total duration."),
        ("Expected Finish:", " P7.1 (Optimal traffic re-entry window)."),
        ("Podium Probability:", " 10%."),
        ("Risk Level:", " HIGH."),
        ("Tactical Verdict:", " BEST DECISION: Allows front traffic to pit, opening a 24s clean-air window for re-entry.")
    ]
    for b_title, b_text in s3_pts:
        p = tf.add_paragraph() if tf.paragraphs[0].text else tf.paragraphs[0]
        r1 = p.add_run()
        r1.text = "• " + b_title
        r1.font.bold = True
        r1.font.size = Pt(9.5)
        r1.font.color.rgb = WHITE
        r2 = p.add_run()
        r2.text = b_text
        r2.font.size = Pt(9)
        r2.font.color.rgb = MUTED

    # Card 3: Stay 5 Laps
    add_card(s9, 8.93, 1.7, 3.6, 5.0, "Tactical Fork: STAY +5 LAPS")
    tb = s9.shapes.add_textbox(Inches(9.18), Inches(2.3), Inches(3.1), Inches(4.2))
    tf = tb.text_frame
    tf.word_wrap = True
    s5_pts = [
        ("Action:", " Extend current stint by 5 laps."),
        ("Expected Time:", " 88m 51s total duration."),
        ("Expected Finish:", " P7.9."),
        ("Podium Probability:", " 10%."),
        ("Risk Level:", " HIGH."),
        ("Tactical Verdict:", " Overcut attempt: tyre hits thermal cliff on lap 4, costing 1.8s in lap pace.")
    ]
    for b_title, b_text in s5_pts:
        p = tf.add_paragraph() if tf.paragraphs[0].text else tf.paragraphs[0]
        r1 = p.add_run()
        r1.text = "• " + b_title
        r1.font.bold = True
        r1.font.size = Pt(9.5)
        r1.font.color.rgb = WHITE
        r2 = p.add_run()
        r2.text = b_text
        r2.font.size = Pt(9)
        r2.font.color.rgb = MUTED

    s9.notes_slide.notes_text_frame.text = (
        "The What-If Simulator provides pit-wall strategists with immediate scenario evaluation. "
        "Here, staying out 3 laps is mathematically proven to be superior to pitting now, "
        "because pitting immediately drops the car into dirty traffic, whereas staying 3 laps opens a clean pit window."
    )

    # =========================================================================
    # SLIDE 10: CLOUD INFRASTRUCTURE & DEPLOYMENT
    # =========================================================================
    s10 = prs.slides.add_slide(blank_layout)
    set_slide_background(s10)
    add_header(s10, "DevOps & Cloud", "Cloud Infrastructure & Production Deployment")

    add_card(s10, 0.8, 1.7, 5.65, 5.0, "Frontend Hosting (Vercel)")
    tb = s10.shapes.add_textbox(Inches(1.05), Inches(2.3), Inches(5.15), Inches(4.2))
    tf = tb.text_frame
    tf.word_wrap = True
    v_pts = [
        ("Global CDN Distribution:", " Deployed on Vercel Edge Network for sub-50ms static asset delivery worldwide."),
        ("Automated CI/CD Pipeline:", " Direct integration with GitHub; pushes to main automatically trigger Vite production builds and atomic deployments."),
        ("Zero Server Maintenance:", " Serverless client architecture handles thousands of concurrent users with zero infrastructure scaling overhead."),
        ("Environment Variable Management:", " Securely points to the production backend via VITE_API_URL environment configuration.")
    ]
    for b_title, b_text in v_pts:
        p = tf.add_paragraph() if tf.paragraphs[0].text else tf.paragraphs[0]
        r1 = p.add_run()
        r1.text = "• " + b_title
        r1.font.bold = True
        r1.font.size = Pt(9.5)
        r1.font.color.rgb = WHITE
        r2 = p.add_run()
        r2.text = b_text
        r2.font.size = Pt(9)
        r2.font.color.rgb = MUTED

    add_card(s10, 6.85, 1.7, 5.65, 5.0, "Backend & Database (Render)")
    tb = s10.shapes.add_textbox(Inches(7.1), Inches(2.3), Inches(5.15), Inches(4.2))
    tf = tb.text_frame
    tf.word_wrap = True
    r_pts = [
        ("Python 3.11 Web Service:", " Hosted on Render running containerized Uvicorn ASGI workers for persistent ML execution."),
        ("Managed PostgreSQL Instance:", " Fully managed PostgreSQL database with encrypted SSL connections and automated backups."),
        ("Infrastructure-as-Code (render.yaml):", " Blueprint deployment provisioning database, web service, and environment variables with one click."),
        ("Production Health Checks:", " Automated health monitoring route (/api/health) for zero-downtime rolling deploys.")
    ]
    for b_title, b_text in r_pts:
        p = tf.add_paragraph() if tf.paragraphs[0].text else tf.paragraphs[0]
        r1 = p.add_run()
        r1.text = "• " + b_title
        r1.font.bold = True
        r1.font.size = Pt(9.5)
        r1.font.color.rgb = WHITE
        r2 = p.add_run()
        r2.text = b_text
        r2.font.size = Pt(9)
        r2.font.color.rgb = MUTED

    s10.notes_slide.notes_text_frame.text = (
        "We chose a decoupled cloud setup. Vercel is ideal for React/Vite client delivery, "
        "while Render provides the persistent Python runtime and managed PostgreSQL database needed for XGBoost and Monte Carlo simulations."
    )

    # =========================================================================
    # SLIDE 11: VERIFICATION & TESTING MATRIX
    # =========================================================================
    s11 = prs.slides.add_slide(blank_layout)
    set_slide_background(s11)
    add_header(s11, "Quality Assurance", "System Verification, Testing & Anti-Leakage Audit")

    add_card(s11, 0.8, 1.7, 5.65, 5.0, "Rigorous Data & ML Audits")
    tb = s11.shapes.add_textbox(Inches(1.05), Inches(2.3), Inches(5.15), Inches(4.2))
    tf = tb.text_frame
    tf.word_wrap = True
    t_pts = [
        ("Zero Data Leakage Audit:", " Formally audited via phase12_leakage_audit.py. Confirmed that no future-lap metrics or whole-race averages contaminate feature vectors during training."),
        ("Mock Isolation Audit:", " Confirmed via audit_mock_usage.py that all API endpoints serve live predictions from Kaggle-trained .joblib pipelines rather than mock fallbacks."),
        ("Model Unpickling Shims:", " Implemented unpickler shims (_RemainderColsList) ensuring 100% backwards compatibility between development and Linux production runtimes."),
        ("Vectorized Benchmark Tests:", " Confirmed 1,000 Monte Carlo runs execute in under 120ms.")
    ]
    for b_title, b_text in t_pts:
        p = tf.add_paragraph() if tf.paragraphs[0].text else tf.paragraphs[0]
        r1 = p.add_run()
        r1.text = "• " + b_title
        r1.font.bold = True
        r1.font.size = Pt(9.5)
        r1.font.color.rgb = WHITE
        r2 = p.add_run()
        r2.text = b_text
        r2.font.size = Pt(9)
        r2.font.color.rgb = MUTED

    add_card(s11, 6.85, 1.7, 5.65, 5.0, "Frontend & API Integration Matrix")
    tb = s11.shapes.add_textbox(Inches(7.1), Inches(2.3), Inches(5.15), Inches(4.2))
    tf = tb.text_frame
    tf.word_wrap = True
    f_pts = [
        ("Formal E2E Test Matrix:", " Passed formal end-to-end integration tests (test_api_core_integration.py and test_api_e2e.py)."),
        ("TypeScript Static Type Safety:", " 0 compile-time errors across all components, interfaces, and API client definitions."),
        ("CORS Security Verification:", " Strictly configured origins allowing authenticated client requests while blocking untrusted origins."),
        ("Vite Production Build:", " Successfully built in 3.48s (client) and 806ms (SSR Nitro) with zero bundle warnings.")
    ]
    for b_title, b_text in f_pts:
        p = tf.add_paragraph() if tf.paragraphs[0].text else tf.paragraphs[0]
        r1 = p.add_run()
        r1.text = "• " + b_title
        r1.font.bold = True
        r1.font.size = Pt(9.5)
        r1.font.color.rgb = WHITE
        r2 = p.add_run()
        r2.text = b_text
        r2.font.size = Pt(9)
        r2.font.color.rgb = MUTED

    s11.notes_slide.notes_text_frame.text = (
        "Academic and industry projects must stand up to rigorous verification. "
        "We performed automated leakage audits to verify zero temporal contamination in ML training, "
        "and ran comprehensive integration test suites across the API and frontend."
    )

    # =========================================================================
    # SLIDE 12: CONCLUSION, ROADMAP & DEMO
    # =========================================================================
    s12 = prs.slides.add_slide(blank_layout)
    set_slide_background(s12)
    add_header(s12, "Summary & Vision", "Conclusion, Future Roadmap & Live Demonstration")

    add_card(s12, 0.8, 1.7, 5.65, 5.0, "Key Accomplishments")
    tb = s12.shapes.add_textbox(Inches(1.05), Inches(2.3), Inches(5.15), Inches(4.2))
    tf = tb.text_frame
    tf.word_wrap = True
    c_pts = [
        ("Bridged DSA & Real-World ML:", " Combined combinatorial search tree pruning with supervised XGBoost telemetry and stochastic Monte Carlo."),
        ("Sub-Second Decision Support:", " Capable of simulating 1,000 race outcomes and solving Pareto multi-objective frontiers in real time."),
        ("Production Full-Stack Deployment:", " Fully deployed and live on Vercel and Render with managed PostgreSQL."),
        ("Human-Centric Analytics:", " Clean standard duration formatting (hours/minutes/seconds) and integer finish positions designed for pit-wall strategists.")
    ]
    for b_title, b_text in c_pts:
        p = tf.add_paragraph() if tf.paragraphs[0].text else tf.paragraphs[0]
        r1 = p.add_run()
        r1.text = "• " + b_title
        r1.font.bold = True
        r1.font.size = Pt(9.5)
        r1.font.color.rgb = WHITE
        r2 = p.add_run()
        r2.text = b_text
        r2.font.size = Pt(9)
        r2.font.color.rgb = MUTED

    add_card(s12, 6.85, 1.7, 5.65, 5.0, "Future Roadmap & Project Links")
    tb = s12.shapes.add_textbox(Inches(7.1), Inches(2.3), Inches(5.15), Inches(4.2))
    tf = tb.text_frame
    tf.word_wrap = True
    r_pts = [
        ("Live FastF1 Streaming:", " WebSocket stream processing during official FIA live race weekends."),
        ("Game-Theoretic Response Networks:", " Multi-agent Nash equilibrium modeling of rival pit responses."),
        ("Doppler Weather Radar ML:", " Computer vision precipitation forecasting for micro-climate rain onset."),
        ("GitHub Repositories:", " github.com/sanskar620/DSA_F1\n  github.com/sanskar620/strategyiq"),
        ("Live Demo & Q&A:", " Now opening the floor for questions and live system walkthrough.")
    ]
    for b_title, b_text in r_pts:
        p = tf.add_paragraph() if tf.paragraphs[0].text else tf.paragraphs[0]
        r1 = p.add_run()
        r1.text = "• " + b_title
        r1.font.bold = True
        r1.font.size = Pt(9.5)
        r1.font.color.rgb = WHITE
        r2 = p.add_run()
        r2.text = b_text
        r2.font.size = Pt(9)
        r2.font.color.rgb = MUTED

    s12.notes_slide.notes_text_frame.text = (
        "In conclusion, F1 StrategyIQ provides a complete, mathematically grounded decision-support system. "
        "All code, documentation, and trained models are open-source on GitHub. "
        "Thank you! I am now ready for questions and a live demo of the application."
    )

    # Save presentation
    prs.save(output_path)
    print(f"[SUCCESS] Created presentation: {output_path}")

if __name__ == "__main__":
    create_deck()
