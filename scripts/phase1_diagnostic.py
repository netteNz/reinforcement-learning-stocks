#!/usr/bin/env python3
"""
Phase 1 Diagnostic: Current behavior analysis + Phase 1 infrastructure layout.

Run from repo root:
  python scripts/phase1_diagnostic.py
"""

import json
import pandas as pd
import math
from pathlib import Path

# Gate thresholds (from agent-api/api/gates.py)
THRESHOLDS = {
    "g1": ("test_actionable_accuracy", ">=", 0.525),
    "g2": ("test_trade_win_rate", ">=", 0.50),
    "g3": ("test_alpha_vs_qqq", ">=", 0.0005),
    "g4": ("g4_drift", "<=", 0.05),
    "g5": ("test_return_cv_by_config", "<", 0.50),
    "g6": ("test_trade_rate", "range", (0.40, 1.00)),
}

def evaluate_gate(row, gate_name):
    """Evaluate a single gate for a row."""
    col, op, thresh = THRESHOLDS[gate_name]

    # Compute g4_drift if not present
    if gate_name == "g4" and "g4_drift" not in row:
        val_acc = row.get("val_actionable_accuracy")
        test_acc = row.get("test_actionable_accuracy")
        if val_acc is not None and test_acc is not None:
            row["g4_drift"] = abs(val_acc - test_acc)
        else:
            return None

    value = row.get(col)
    if value is None or (isinstance(value, float) and math.isnan(value)):
        return None

    value = float(value)

    if op == ">=":
        return value >= thresh
    elif op == "<=":
        return value <= thresh
    elif op == "<":
        return value < thresh
    elif op == "range":
        lo, hi = thresh
        return lo <= value <= hi
    return None

def main():
    leaderboard_path = Path("data/experiment_leaderboard_history.csv")
    ensemble_path = Path("staging/models/ensemble_config.json")

    print("=" * 80)
    print("PHASE 1 DIAGNOSTIC: Current Behavior Analysis")
    print("=" * 80)
    print()

    # Load leaderboard
    df = pd.read_csv(leaderboard_path)
    print(f"[OK] Leaderboard loaded: {len(df)} rows")
    print()

    # Load ensemble config
    with open(ensemble_path) as f:
        ensemble_cfg = json.load(f)

    print("PROMOTED TICKERS (from ensemble_config.json):")
    print("-" * 80)
    promoted = {k: v for k, v in ensemble_cfg.items() if v.get("production_ready") is True}
    for ticker, cfg in promoted.items():
        seeds = cfg.get("active_seeds", [])
        sharpe = cfg.get("top_3_mean_sharpe", "N/A")
        min_hold = cfg.get("min_hold_bars", 1)
        print(f"  {ticker.upper():6} | Seeds: {seeds} | Sharpe: {sharpe} | min_hold: {min_hold}")
    print()

    # Analyze gate pass rates by ticker
    print("GATE PASS RATES (6-Gate Framework):")
    print("-" * 80)

    for ticker in ["nvda", "amd", "mu"]:
        ticker_df = df[df["ticker"].str.lower() == ticker.lower()]
        if ticker_df.empty:
            print(f"  {ticker.upper():6} | No runs found")
            continue

        gate_results = {g: [] for g in ["g1", "g2", "g3", "g4", "g5", "g6"]}

        for _, row in ticker_df.iterrows():
            for gate in gate_results:
                result = evaluate_gate(dict(row), gate)
                gate_results[gate].append(result)

        passed = {g: sum(1 for r in results if r is True) for g, results in gate_results.items()}
        total = {g: sum(1 for r in results if r is not None) for g, results in gate_results.items()}

        pass_rates = {}
        for g in gate_results:
            if total[g] > 0:
                pass_rates[g] = f"{passed[g]}/{total[g]} ({100*passed[g]/total[g]:.0f}%)"
            else:
                pass_rates[g] = "N/A"

        print(f"  {ticker.upper():6} | G1: {pass_rates['g1']:12} | G2: {pass_rates['g2']:12} | "
              f"G3: {pass_rates['g3']:12} | G4: {pass_rates['g4']:12}")
        print(f"         | G5: {pass_rates['g5']:12} | G6: {pass_rates['g6']:12}")
        print()

    # Current issue: buy-skewed behavior
    print("PHASE 1 FOCUS: Buy-Skew & Exit Weakness")
    print("-" * 80)
    print("""
Recent diagnostics show:
  - Policy is too long-biased (favors Buy over Hold/Flat)
  - Exit intent is weak; policy struggles to close positions
  - Trade rates are either very high (MU: 95.6%) or low-entropy

Phase 1 Tasks:
  1. Add telemetry for raw actor logits (before masking)
  2. Log policy entropy H(pi) per bar per ticker
  3. Log critic value V(s) and value estimation error
  4. Capture advantage traces around cooldown windows
  5. Measure forced-long periods (min_hold_bars constraint)
  6. Save per-run audit reports (data/audit/phase1_runs/)

Next: Run baseline NVDA sweep with enhanced telemetry.
""")
    print()

    # Infrastructure checklist
    print("PHASE 1 INFRASTRUCTURE CHECKLIST:")
    print("-" * 80)
    audit_dir = Path("data/audit/phase1_runs")
    audit_dir.mkdir(parents=True, exist_ok=True)

    required_dirs = [
        ("data/audit/phase1_runs", "Per-run telemetry and entropy logs"),
        ("data/audit/logits", "Raw actor logits snapshots"),
        ("data/audit/advantages", "Advantage trace analysis"),
    ]

    for dir_path, purpose in required_dirs:
        p = Path(dir_path)
        p.mkdir(parents=True, exist_ok=True)
        status = "[OK]" if p.exists() else "[FAIL]"
        print(f"  {status} {dir_path:40} — {purpose}")

    print()
    print("=" * 80)
    print("Ready for Phase 1. Next: Run baseline NVDA sweep with telemetry.")
    print("=" * 80)

if __name__ == "__main__":
    main()
