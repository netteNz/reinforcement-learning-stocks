# gates.py
THRESHOLDS = {
    "g1": ("test_actionable_accuracy", ">=", 0.525),
    "g2": ("test_trade_win_rate",       ">=", 0.50),
    "g3": ("test_alpha_vs_qqq",         ">=", 0.0005),
    "g4": ("g4_drift",                  "<=", 0.05),
    "g5": ("clean_cv",                  "<",  0.50),
    "g6_low":  ("test_trade_rate",      ">=", 0.40),
    "g6_high": ("test_trade_rate",      "<=", 1.00),
}

def evaluate_gates(row: dict) -> dict:
    results = {}
    for gate, (col, op, thresh) in THRESHOLDS.items():
        val = row.get(col)
        if val is None:
            results[gate] = {"pass": None, "value": None, "threshold": thresh}
            continue
        if op == ">=":  passed = val >= thresh
        elif op == "<=": passed = val <= thresh
        elif op == "<":  passed = val < thresh
        else:            passed = None
        results[gate] = {"pass": passed, "value": val, "threshold": thresh}
    # G6 is a range — both sub-checks must pass
    g6 = results.pop("g6_low")["pass"] and results.pop("g6_high")["pass"]
    results["g6"] = {
        "pass": g6,
        "value": row.get("test_trade_rate"),
        "threshold": "[0.40, 1.00]"
    }
    return results