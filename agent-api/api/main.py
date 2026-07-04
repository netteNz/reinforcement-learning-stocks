# main.py
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from data_loader import load_leaderboard, load_ensemble_config, load_snapshot_for_label
from gates import evaluate_gates
import math

app = FastAPI(title="quant-experiment-agent API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],   # tighten this when exposing beyond localhost
    allow_methods=["GET"],
    allow_headers=["*"],
)

def _safe_row(row: dict) -> dict:
    """Replace NaN/inf so JSON serialization doesn't blow up."""
    return {k: (None if isinstance(v, float) and not math.isfinite(v) else v)
            for k, v in row.items()}

@app.get("/health")
def health():
    df = load_leaderboard()
    return {"status": "ok", "leaderboard_rows": len(df)}

@app.get("/runs/{ticker}")
def runs_by_ticker(ticker: str, limit: int = 50):
    """All leaderboard rows for a ticker, newest run_label first."""
    df = load_leaderboard()
    col = "ticker" if "ticker" in df.columns else next(
        (c for c in df.columns if "ticker" in c.lower()), None)
    if col is None:
        raise HTTPException(500, "ticker column not found in leaderboard")
    rows = df[df[col].str.upper() == ticker.upper()]
    if rows.empty:
        raise HTTPException(404, f"No runs found for ticker={ticker}")
    return {
        "ticker": ticker.upper(),
        "count": len(rows),
        "runs": [_safe_row(r) for r in rows.tail(limit).to_dict("records")]
    }

@app.get("/runs/label/{run_label}")
def runs_by_label(run_label: str):
    """All rows for a specific run_label — exact match first, snapshot fallback."""
    df = load_leaderboard()
    col = "run_label" if "run_label" in df.columns else next(
        (c for c in df.columns if "label" in c.lower()), None)
    if col is None:
        raise HTTPException(500, "run_label column not found in leaderboard")
    rows = df[df[col] == run_label]
    source = "leaderboard_history"
    if rows.empty:
        # fallback: try loading from experiment_snapshots directly
        snap = load_snapshot_for_label(run_label)
        if snap is None:
            raise HTTPException(404, f"run_label={run_label!r} not found in leaderboard or snapshots")
        rows = snap
        source = "experiment_snapshots"
    return {
        "run_label": run_label,
        "source": source,
        "count": len(rows),
        "rows": [_safe_row(r) for r in rows.to_dict("records")]
    }

@app.get("/gates/{gate_name}/failures")
def gate_failures(gate_name: str, ticker: str | None = None):
    """
    Cross-ticker gate failure report. gate_name: g1-g6.
    Optional ?ticker= filter. Returns only rows that failed the gate.
    """
    gate_name = gate_name.lower()
    df = load_leaderboard()
    if ticker:
        col = "ticker" if "ticker" in df.columns else None
        if col:
            df = df[df[col].str.upper() == ticker.upper()]

    failures = []
    for row in df.to_dict("records"):
        gate_results = evaluate_gates(row)
        if gate_name not in gate_results:
            raise HTTPException(400, f"Unknown gate: {gate_name}. Valid: g1-g6")
        gate = gate_results[gate_name]
        if gate["pass"] is False:
            failures.append({
                **_safe_row(row),
                f"{gate_name}_value": gate["value"],
                f"{gate_name}_threshold": gate["threshold"],
            })
    return {
        "gate": gate_name,
        "ticker_filter": ticker,
        "failure_count": len(failures),
        "failures": failures
    }

@app.get("/ensemble/config")
def ensemble_config():
    """Current ensemble_config.json — active seeds, production status per ticker."""
    return load_ensemble_config()