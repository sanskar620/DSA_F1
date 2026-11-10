# F1 Strategy Hub (77)

F1 StrategyIQ — Frontend Development Prompt

Build ONLY the frontend/UI for the project below.

Project

F1 StrategyIQ: Data-Driven Race Strategy Optimization & Dynamic Pit-Wall Decision Support System

The final application will eventually use:

Python

Streamlit — frontend

FastAPI — backend

PostgreSQL — database

Pandas / NumPy — data processing

Scikit-learn / XGBoost — ML

Plotly — interactive visualizations

IMPORTANT SCOPE RULE

For this task, build ONLY the Streamlit frontend.

DO NOT implement:

FastAPI backend

PostgreSQL

ML models

model training

FastF1 API integration

Jolpica API integration

authentication

deployment

real-time F1 data streaming

Use mock/sample data so the frontend is fully functional and visually demonstrable.

The backend will be connected later.

1. Main Goal

Create a polished, modern, interactive F1 strategy analytics dashboard.

The UI should feel like a professional F1 race strategy / data analytics dashboard, not a generic Streamlit app.

It should demonstrate:

Analyze → Predict → Simulate → Optimize → Decide → Re-evaluate

The frontend should allow the user to select a race, driver and race scenario, then visualize predictions, strategy comparisons and Pit-Wall recommendations.

2. Tech Requirements

Use:

Python

Streamlit

Pandas

NumPy

Plotly

Use Streamlit components wherever possible.

Keep dependencies minimal.

Create:

app.py

and, only if genuinely necessary:

components/

data/

utils/

Do NOT create a large unnecessary architecture.

Keep the project simple and easy to connect to FastAPI later.

3. UI Design

Create a premium motorsport/data-science interface.

Design direction:

Dark F1-inspired dashboard

Clean modern cards

Strong typography

Minimal unnecessary decoration

High information density without looking cluttered

Responsive layout

Professional charts

Clear hierarchy

Avoid:

excessive animations

unnecessary gradients

huge images

complicated CSS

excessive icons

unnecessary pages

heavy frontend frameworks

The application should remain lightweight.

4. Sidebar

Create a sidebar containing:

Race Configuration

Season:

2024

Grand Prix:

Bahrain

Monaco

Silverstone

Spa

Monza

Singapore

Suzuka

Interlagos

Driver:

Charles Leclerc

Max Verstappen

Lando Norris

Oscar Piastri

Lewis Hamilton

Starting Tyre:

Soft

Medium

Hard

Risk Preference:

Conservative

Balanced

Aggressive

Add:

RUN ANALYSIS

button.

Use Streamlit widgets.

5. Dashboard Navigation

Use a simple Streamlit navigation system.

Pages:

Overview

Race Analysis

Tyre Intelligence

Strategy Optimizer

Dynamic Pit-Wall

What-If Simulator

Do not create more pages unless necessary.

6. Overview Page

Create a professional dashboard landing page.

Header:

F1 StrategyIQ

Race Strategy Intelligence Platform

Show selected race:

2024 Bahrain Grand Prix

Create KPI cards:

Current Lap

28 / 57

Position

P5

Current Tyre

MEDIUM

Tyre Age

18 Laps

Gap Ahead

2.1 sec

Gap Behind

1.4 sec

Add a prominent recommendation card:

PIT NOW

Confidence

84%

Recommended Tyre

MEDIUM

Reason:

High tyre degradation + favorable pit window

Below it show:

Race Position Chart

Interactive Plotly line chart.

X-axis:

Lap

Y-axis:

Position

Reverse the Y-axis because P1 should appear at the top.

Show the driver's position throughout the race.

7. Race Analysis Page

Create interactive visual analysis.

Include:

Chart 1 — Lap Time

Actual lap time vs predicted lap time.

Use Plotly.

Chart 2 — Position

Driver position throughout the race.

Chart 3 — Gap

Gap to car ahead and gap to car behind.

Chart 4 — Sector Performance

Compare Sector 1, Sector 2 and Sector 3.

Driver Comparison

Allow the user to select another driver and compare:

average lap time

best lap

average position

tyre stints

Use charts instead of only text.

8. Tyre Intelligence Page

Create a dedicated tyre analytics dashboard.

Top cards:

Current Compound

MEDIUM

Tyre Age

18

Estimated Degradation

0.09 sec/lap

Projected Useful Window

~5 laps

Create:

Tyre Degradation Curve

X:

Tyre Age

Y:

Lap Time

Show different compounds.

Compound Comparison

Compare:

SOFT

MEDIUM

HARD

using an interactive Plotly chart.

Stint Timeline

Show:

Lap 1 ───────── Lap 20

MEDIUM

Lap 21 ───────── Lap 38

HARD

Lap 39 ───────── Lap 57

MEDIUM

Make it visually clear which compound was used in each stint.

9. Strategy Optimizer Page

This is one of the most important pages.

Show candidate strategies:

Medium → Hard

Medium → Medium → Hard

Soft → Medium → Hard

Medium → Hard → Soft

Create a comparison table with:

StrategyExpected TimeExpected FinishPodium %Win %RiskM → H92:18P442%18%LowM → M → H92:05P351%24%MediumS → M → H92:31P535%12%High

Highlight the recommended strategy.

Create visualizations:

Strategy Race Time

Bar chart.

Podium Probability

Bar chart.

Finishing Position Distribution

Histogram/bar chart.

Strategy Timeline

Visually show pit laps and tyre compounds.

10. Dynamic Pit-Wall Page

Make this page look like a race-control decision dashboard.

Top section:

RACE LIVE REPLAY

Bahrain GP

Lap 28 / 57

Show current state:

Position       P5

Tyre           Medium

Tyre Age       18

Gap Ahead      2.1s

Gap Behind     1.4s

Recent Pace    1:34.8

Degradation    HIGH

Safety Car     YES

Then create a large recommendation panel:

🚨 PIT NOW

Confidence: 84%

Switch to:

MEDIUM

Why?

• High tyre degradation

• Safety Car reduces pit-loss

• Good gap protection

• Fresh tyre projected to be faster

Below it show:

Decision History

Example:

Lap 20 → STAY OUT

Lap 23 → STAY OUT

Lap 25 → PIT WINDOW

Lap 28 → PIT NOW

Visualize this as a timeline.

Race Replay Controls

Add:

◀ Previous Lap

▶ Next Lap

⏯ Play/Pause

Also provide a slider:

Current Lap: 28

When the lap changes, update the mock race state and charts.

IMPORTANT:

This is a historical race replay using mock data, NOT real-time F1 streaming.

11. What-If Simulator

Create interactive scenario controls.

Inputs:

Current Lap

Pit Decision

Tyre Choice

Laps to Stay Out

Safety Car

Weather Scenario

Risk Preference

Example buttons:

PIT NOW

STAY 3 LAPS

STAY 5 LAPS

After changing the scenario, display:

Scenario Comparison

                 PIT NOW    STAY +3    STAY +5

Race Time        92:15      92:28      92:42

Expected Pos.      P3         P4         P5

Podium             72%        58%        41%

Risk               LOW       MEDIUM      HIGH

Create visual comparison charts.

This page should demonstrate that the system is a decision-support tool, not simply a prediction model.

12. Mock Data

Generate realistic-looking synthetic/mock data locally.

Examples:

57 race laps

position changes

lap times

tyre ages

compounds

gaps

degradation

pit stops

Safety Car events

predicted values

Do NOT download data from the internet.

Do NOT call external APIs.

Do NOT implement FastF1 yet.

The mock data should be deterministic using a fixed random seed so the dashboard behaves consistently.

13. Backend Integration Preparation

Even though the backend is NOT being implemented now, structure the frontend so it can later consume API responses.

For example, create simple placeholder functions:

get_race_data()

get_driver_data()

predict_lap_time()

predict_tyre_degradation()

optimize_strategy()

get_pitwall_decision()

For now these functions should return mock data.

Later these functions can be replaced with FastAPI requests.

Do NOT build the FastAPI server now.

14. Visual Output Requirements

The application must contain substantial visual analytics.

Minimum visualizations:

Race position line chart

Actual vs predicted lap-time chart

Gap ahead/behind chart

Tyre degradation curve

Compound comparison

Tyre stint timeline

Strategy race-time comparison

Podium probability chart

Win probability chart

Finishing-position distribution

Pit-window timeline

Dynamic Pit-Wall decision timeline

What-if scenario comparison

Use Plotly for interactive charts.

Charts should have:

hover information

clear axis labels

useful legends

readable titles

consistent formatting

15. Important UX Rule

Do not dump every metric onto one page.

Use:

KPI cards

tabs

columns

expandable sections

charts

tables

recommendation cards

Maintain visual hierarchy.

16. Performance / Token / Credit Optimization

This is VERY IMPORTANT.

Keep the implementation lightweight.

DO:

Reuse components

Reuse mock datasets

Use simple deterministic calculations

Use Plotly

Keep CSS minimal

Keep the number of files low

Write concise code

Use functions

Cache static/mock data with Streamlit caching

Avoid unnecessary refactoring

DO NOT:

Build backend

Build database

Train ML models

Download F1 datasets

Call external APIs

Build authentication

Build Docker

Build deployment configuration

Add React

Add JavaScript frameworks

Add unnecessary animations

Generate hundreds of lines of unnecessary CSS

Create unnecessary documentation files

17. Development Strategy

Build the frontend in this order:

Phase 1

Create:

app.py

sidebar

navigation

Overview page

mock data

KPI cards

STOP and verify it runs.

Phase 2

Add:

Race Analysis

Tyre Intelligence

Plotly charts

Verify again.

Phase 3

Add:

Strategy Optimizer

strategy comparison

probability visualizations

Verify again.

Phase 4

Add:

Dynamic Pit-Wall

race replay slider

decision timeline

Verify again.

Phase 5

Add:

What-If Simulator

final styling

performance cleanup

Do not attempt all phases blindly in one generation.

18. Final Acceptance Criteria

The frontend is successful if:

streamlit run app.py starts successfully.

User can select a race and driver.

Dashboard updates based on selections.

All six pages work.

Mock data is displayed realistically.

Charts are interactive.

Strategy comparison works.

Pit-Wall recommendation changes when race-state inputs change.

What-if scenarios produce different outputs.

UI looks like a professional F1 analytics dashboard.

No external API is required.

No backend/database is required yet.

Code is small, readable and easy to connect to FastAPI later.

MOST IMPORTANT

Do not over-engineer.

This is the frontend prototype only.

Prioritize:

Beautiful UI + meaningful interaction + strong visual analytics + clean architecture for future FastAPI integration.

Do not spend tokens/credits implementing functionality that belongs to the backend.

This project was built with [Lovable](https://lovable.dev).

## Build with Lovable

Continue developing this project in the [Lovable editor](https://lovable.dev/projects/ae87b527-066e-4eab-9797-1a338bee2859).

- **Ship faster**: describe what you want to build and Lovable handles the code.
- **Stay in sync**: every change made in Lovable is committed straight to this repository.
- **Full ownership**: this code is yours. Push to `main` on GitHub and your changes sync back into Lovable, ready for your next prompt.

## Development

Prefer working locally? You need Node.js and npm — [install with nvm](https://github.com/nvm-sh/nvm#installing-and-updating).

```sh
git clone <this-repository-url>
cd <repository-name>
npm i
npm run dev
```
