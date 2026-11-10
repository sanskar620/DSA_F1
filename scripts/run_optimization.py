import os
import sys
import pandas as pd
import matplotlib.pyplot as plt

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.optimization.optimizer import optimize_strategies
from backend.optimization.validation import validate_strategies
from backend.optimization.sensitivity import run_sensitivity_analysis

def main():
    print("=== Phase 8: Strategy Optimization Engine ===")
    
    # 1. Load Phase 7 outputs
    mc_path = "data/processed/monte_carlo/strategy_summary.csv"
    if not os.path.exists(mc_path):
        print("\n[ERROR] Phase 7 Monte Carlo results are required before strategy optimization.")
        print(f"Could not find {mc_path}")
        sys.exit(1)
        
    df_mc = pd.read_csv(mc_path)
    if df_mc.empty:
        print("[ERROR] Phase 7 results are empty.")
        sys.exit(1)
        
    # 2. Feasibility Validation (Phase 6 Constraints)
    # We pass a dummy initial_lap since this was already filtered in Phase 6/7,
    # but the architectural requirement enforces a validation step here.
    df_valid = validate_strategies(df_mc, initial_lap=1, total_laps=58)
    
    print(f"Loaded {len(df_mc)} Monte Carlo strategies. {len(df_valid)} passed feasibility checks.")
    
    # 3. Optimize under BALANCED objective
    print("\nRunning Optimization (BALANCED Objective)...")
    opt_result = optimize_strategies(df_valid, objective_name="BALANCED")
    
    winner = opt_result['recommended_strategy']
    df_results = opt_result['full_results']
    
    print(f"\n=> RECOMMENDED STRATEGY: {winner}")
    for reason in opt_result['reasoning']:
        print(f"   - {reason}")
        
    print("\nTop 3 Strategies by Score:")
    print(df_results[['Strategy', 'Objective Score', 'Mean Race Time', 'Mean Finish Position', 'Dominated']].head(3).to_string(index=False))
    
    # 4. Sensitivity Analysis
    print("\nRunning Sensitivity Analysis across objective profiles...")
    sens_result = run_sensitivity_analysis(df_valid)
    print(f"Recommendation Robustness: {sens_result['recommendation_robustness']}")
    for obj, strat in sens_result['sensitivity_map'].items():
        print(f"  - {obj}: {strat}")
        
    # 5. Visualizations
    os.makedirs("figures/phase8", exist_ok=True)
    
    # Plot: Race Time vs Risk (Pareto visualization)
    plt.figure(figsize=(10, 6))
    plt.scatter(df_results['Risk'], df_results['Mean Race Time'], color='blue', alpha=0.7)
    
    # Highlight Winner
    winner_row = df_results.iloc[0]
    plt.scatter(winner_row['Risk'], winner_row['Mean Race Time'], color='red', marker='*', s=200, label=f'Winner ({winner})')
    
    # Label a few top points
    for i in range(min(3, len(df_results))):
        plt.annotate(df_results.iloc[i]['Strategy'], 
                     (df_results.iloc[i]['Risk'], df_results.iloc[i]['Mean Race Time']),
                     xytext=(5, 5), textcoords='offset points')
                     
    plt.title("Strategy Pareto Front: Risk vs Expected Race Time")
    plt.xlabel("Risk (Std Dev of Race Time)")
    plt.ylabel("Expected Race Time (Lower is Better)")
    plt.grid(True, alpha=0.3)
    plt.legend()
    plt.savefig("figures/phase8/risk_vs_time.png")
    plt.close()
    
    # 6. Reporting
    os.makedirs("reports", exist_ok=True)
    report_md = f"""# Phase 8: Optimization Report

## 1. Overview
Evaluated {len(df_valid)} valid strategies from Phase 7 using the BALANCED weighted objective.

## 2. Recommendation
**Selected Strategy**: {winner}
**Objective Score**: {opt_result['score']:.3f}

### Reasoning:
"""
    for reason in opt_result['reasoning']:
        report_md += f"- {reason}\n"
        
    report_md += f"""
## 3. Baseline Comparison
Compared against the baseline strategy (**{opt_result['baseline']['strategy']}**):
- Expected Time Difference: {opt_result['baseline']['time_diff']:.2f}s
- Expected Position Difference: {opt_result['baseline']['pos_diff']:.1f} positions

## 4. Sensitivity Analysis
Robustness: **{sens_result['recommendation_robustness']}**

Optimal Strategies under different configurations:
"""
    for obj, strat in sens_result['sensitivity_map'].items():
        report_md += f"- **{obj}**: {strat}\n"
        
    with open("reports/phase8_optimization_report.md", "w") as f:
        f.write(report_md)
        
    print("\nOptimization complete. Report saved to reports/phase8_optimization_report.md")
    print("Visualizations saved to figures/phase8/")

if __name__ == "__main__":
    main()
