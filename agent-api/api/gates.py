"""
Gate thresholds and pass/fail evaluation logic.

Thresholds must stay in sync with evaluate_sweep.py — this is the single
source of truth for the agent API side. If evaluate_sweep.py changes a
threshold, update THRESHOLDS here too.

6-Gate promotion framework (Binary PPO):
  G1  test_actionable_accuracy  >= 0.525
  G2  test_trade_win_rate       >= 0.50
  G3  test_alpha_vs_qqq         >= 0.0005
  G4  |val_acc - test_acc|      <= 0.05   (drift check)
  G5  clean_cv                  <  0.50   (active seeds only)
  G6  test_trade_rate           in [0.40, 1.00]
"""

import math

THRESHOLDS: dict[str, tuple] = {
    "g1": ("test_actionable_accuracy",  ">=", 0.525),
    "g2": ("test_trade_win_rate",       ">=", 0.50),
    "g3": ("test_alpha_vs_qqq",         ">=", 0.0005),
    "g4": ("g4_drift",                  "<=", 0.05),
    # G5: authoritative metric is clean_cv (active seeds only, collapsed filtered),
    # computed by evaluate_sweep.py and not present in the main leaderboard CSV.
    # Using test_return_cv_by_config (raw, unfiltered) as fallback — raw CV is
    # higher than clean_cv so this is conservative (harder to pass than the real gate).
    # If evaluate_sweep.py output is available, prefer querying that directly.
    "g5": ("test_return_cv_by_config",  "<",  0.50),
    "g6": ("test_trade_rate",           "range", (0.40, 1.00)),
}

GATE_DESCRIPTIONS = {
    "g1": "Actionable accuracy >= 0.525",
    "g2": "Trade win rate >= 0.50",
    "g3": "Alpha vs QQQ >= 0.0005",
    "g4": "Val/test accuracy drift <= 0.05",
    "g5": "Clean CV (active seeds) < 0.50",
    "g6": "Trade rate in [0.40, 1.00]",
}


def _eval_op(value: float, op: str, threshold) -> bool:
    if op == ">=":
        return value >= threshold
    if op == "<=":
        return value <= threshold
    if op == "<":
        return value < threshold
    if op == ">":
        return value > threshold
    if op == "range":
        lo, hi = threshold
        return lo <= value <= hi
    raise ValueError(f"Unknown operator: {op!r}")


def evaluate_gates(row: dict) -> dict[str, dict]:
    """
    Evaluate all 6 gates for a single leaderboard row.

    Returns dict keyed g1-g6, each with:
      pass      bool | None  (None = column missing or NaN from row)
      value     float | None
      threshold str | float
      description str
    """
    results = {}

    for gate, (col, op, thresh) in THRESHOLDS.items():
        value = row.get(col)
        description = GATE_DESCRIPTIONS[gate]

        # Treat both None and NaN as missing — NaN must be checked explicitly
        # because float('nan') is not None, and nan < 0.50 evaluates False in
        # Python rather than raising, silently turning missing data into failures.
        is_missing = value is None or (isinstance(value, float) and math.isnan(value))

        if is_missing:
            results[gate] = {
                "pass": None,
                "value": None,
                "threshold": str(thresh),
                "description": description,
                "note": f"Column '{col}' is null/NaN for this row",
            }
            continue

        try:
            passed = _eval_op(float(value), op, thresh)
        except (TypeError, ValueError):
            passed = None

        results[gate] = {
            "pass": passed,
            "value": value,
            "threshold": str(thresh),
            "description": description,
        }

    return results


def gates_summary(gate_results: dict) -> dict:
    """Compact pass/fail summary — useful for agent reasoning output."""
    passed = [g for g, r in gate_results.items() if r["pass"] is True]
    failed = [g for g, r in gate_results.items() if r["pass"] is False]
    missing = [g for g, r in gate_results.items() if r["pass"] is None]
    return {
        "promoted": len(failed) == 0 and len(missing) == 0,
        "passed": passed,
        "failed": failed,
        "missing_data": missing,
        "pass_count": len(passed),
        "fail_count": len(failed),
    }