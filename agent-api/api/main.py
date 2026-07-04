"""
quant-experiment-agent API

Endpoints:
  GET /health                          — liveness + leaderboard row count
  GET /runs/{ticker}                   — all runs for a ticker
  GET /runs/label/{run_label}          — rows for a specific run_label
  GET /gates/{gate_name}/failures      — cross-ticker gate failure report
  GET /ensemble/config                 — current ensemble_config.json
  POST /cache/invalidate               — reload leaderboard + config from disk

Run from agent-api/ directory:
  uvicorn main:app --reload --port 8001
"""

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware

from data_loader import (
    load_leaderboard,
    load_ensemble_config,
    load_snapshot_for_label,
    invalidate_cache,
    safe_row,
    ticker_col,
    label_col,
)
from gates import evaluate_gates, gates_summary, GATE_DESCRIPTIONS

app = FastAPI(
    title="quant-experiment-agent API",
    description="Structured lookup layer for the Binary PPO trading experiment history.",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],   # tighten when exposing beyond localhost / Pi LAN
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)


# ---------------------------------------------------------------------------
# Health
# ---------------------------------------------------------------------------

@app.get("/health")
def health():
    df = load_leaderboard()
    cfg = load_ensemble_config()
    return {
        "status": "ok",
        "leaderboard_rows": len(df),
        "leaderboard_columns": list(df.columns),
        "ensemble_tickers": list(cfg.keys()),
    }


# ---------------------------------------------------------------------------
# Runs
# ---------------------------------------------------------------------------

@app.get("/runs/{ticker}")
def runs_by_ticker(
    ticker: str,
    limit: int = Query(default=50, le=500),
    run_label: str | None = Query(default=None, description="Filter by run_label"),
):
    """
    All leaderboard rows for a ticker, most recent first.
    Optional ?run_label= to scope to a specific sweep.
    """
    df = load_leaderboard()
    col = ticker_col(df)
    if col is None:
        raise HTTPException(500, "ticker column not found in leaderboard")

    rows = df[df[col].str.upper() == ticker.upper()]
    if run_label:
        lcol = label_col(rows)
        if lcol:
            rows = rows[rows[lcol] == run_label]

    if rows.empty:
        raise HTTPException(404, f"No runs found for ticker={ticker!r}"
                            + (f" run_label={run_label!r}" if run_label else ""))

    records = [safe_row(r) for r in rows.tail(limit).to_dict("records")]
    return {
        "ticker": ticker.upper(),
        "run_label_filter": run_label,
        "count": len(records),
        "runs": records,
    }


@app.get("/runs/label/{run_label}")
def runs_by_label(run_label: str):
    """
    All rows for a specific run_label.
    Tries main leaderboard first; falls back to experiment_snapshots/ on miss.
    """
    df = load_leaderboard()
    lcol = label_col(df)

    rows = df[df[lcol] == run_label] if lcol else df.iloc[0:0]
    source = "leaderboard_history"

    if rows.empty:
        snap = load_snapshot_for_label(run_label)
        if snap is None:
            raise HTTPException(
                404,
                f"run_label={run_label!r} not found in leaderboard or snapshots. "
                f"Check spelling — labels are case-sensitive."
            )
        rows = snap
        source = "experiment_snapshots"

    records = [safe_row(r) for r in rows.to_dict("records")]
    return {
        "run_label": run_label,
        "source": source,
        "count": len(records),
        "rows": records,
    }


# ---------------------------------------------------------------------------
# Gates
# ---------------------------------------------------------------------------

@app.get("/gates")
def list_gates():
    """Available gate names and what they measure."""
    return {"gates": GATE_DESCRIPTIONS}


@app.get("/gates/{gate_name}/failures")
def gate_failures(
    gate_name: str,
    ticker: str | None = Query(default=None, description="Scope to one ticker"),
    run_label: str | None = Query(default=None, description="Scope to one run_label"),
):
    """
    Cross-ticker gate failure report for gate_name (g1–g6).
    Optional ?ticker= and ?run_label= filters.
    Returns only rows that explicitly failed the gate (pass=False).
    Rows with missing gate data are listed separately under missing_data.
    """
    gate_name = gate_name.lower()
    if gate_name not in GATE_DESCRIPTIONS:
        raise HTTPException(
            400,
            f"Unknown gate: {gate_name!r}. Valid values: {list(GATE_DESCRIPTIONS)}"
        )

    df = load_leaderboard()

    if ticker:
        col = ticker_col(df)
        if col:
            df = df[df[col].str.upper() == ticker.upper()]

    if run_label:
        lcol = label_col(df)
        if lcol:
            df = df[df[lcol] == run_label]

    failures, missing = [], []

    for row in df.to_dict("records"):
        gate_results = evaluate_gates(row)
        result = gate_results[gate_name]
        enriched = {
            **safe_row(row),
            f"{gate_name}_value": result["value"],
            f"{gate_name}_threshold": result["threshold"],
        }
        if result["pass"] is False:
            failures.append(enriched)
        elif result["pass"] is None:
            missing.append(enriched)

    return {
        "gate": gate_name,
        "description": GATE_DESCRIPTIONS[gate_name],
        "ticker_filter": ticker,
        "run_label_filter": run_label,
        "failure_count": len(failures),
        "missing_data_count": len(missing),
        "failures": failures,
        "missing_data": missing,
    }


@app.get("/gates/{gate_name}/summary")
def gate_summary_by_ticker(gate_name: str):
    """
    Per-ticker pass rate for a given gate across all leaderboard rows.
    Useful for spotting which tickers consistently struggle with a specific gate.
    """
    gate_name = gate_name.lower()
    if gate_name not in GATE_DESCRIPTIONS:
        raise HTTPException(400, f"Unknown gate: {gate_name!r}")

    df = load_leaderboard()
    col = ticker_col(df)
    if col is None:
        raise HTTPException(500, "ticker column not found")

    summary = {}
    for ticker_val, group in df.groupby(col):
        passed = failed = missing = 0
        for row in group.to_dict("records"):
            result = evaluate_gates(row)[gate_name]
            if result["pass"] is True:   passed  += 1
            elif result["pass"] is False: failed  += 1
            else:                         missing += 1
        total = passed + failed
        summary[ticker_val] = {
            "passed": passed,
            "failed": failed,
            "missing": missing,
            "pass_rate": round(passed / total, 3) if total else None,
        }

    return {
        "gate": gate_name,
        "description": GATE_DESCRIPTIONS[gate_name],
        "by_ticker": summary,
    }


# ---------------------------------------------------------------------------
# Ensemble config
# ---------------------------------------------------------------------------

@app.get("/ensemble/config")
def ensemble_config():
    """Current ensemble_config.json — active seeds and production status per ticker."""
    return load_ensemble_config()


@app.get("/ensemble/config/{ticker}")
def ensemble_config_ticker(ticker: str):
    """Ensemble config for a single ticker."""
    cfg = load_ensemble_config()
    entry = cfg.get(ticker.lower())
    if entry is None:
        raise HTTPException(404, f"ticker={ticker!r} not in ensemble config")
    return {"ticker": ticker.upper(), **entry}


# ---------------------------------------------------------------------------
# Cache management
# ---------------------------------------------------------------------------

@app.post("/cache/invalidate")
def cache_invalidate():
    """Force reload of leaderboard and ensemble config from disk."""
    invalidate_cache()
    df = load_leaderboard()
    return {"status": "reloaded", "leaderboard_rows": len(df)}