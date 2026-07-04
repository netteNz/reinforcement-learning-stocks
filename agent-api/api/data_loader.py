"""
Data loading layer for the quant-experiment-agent API.

Loading strategy:
  - experiment_leaderboard_history.csv is loaded once at first request and
    cached in memory via lru_cache — it's the primary query surface (~1MB).
  - Individual snapshot CSVs under data/experiment_snapshots/ are loaded
    on-demand only when a run_label query misses the main leaderboard.
    Do NOT load all 1026 snapshot files at startup.
  - ensemble_config.json is also cached — call invalidate_cache() if you
    need to reload after a restage.
"""

import json
import math
import pandas as pd
from functools import lru_cache
from pathlib import Path
from config import (
    LEADERBOARD_CSV,
    LEADERBOARD_HIST_CSV,
    ENSEMBLE_CONFIG_JSON,
    SNAPSHOTS_DIR,
)


# ---------------------------------------------------------------------------
# Cache invalidation — call after a restage or config update
# ---------------------------------------------------------------------------

def invalidate_cache():
    load_leaderboard.cache_clear()
    load_ensemble_config.cache_clear()


# ---------------------------------------------------------------------------
# Loaders
# ---------------------------------------------------------------------------

@lru_cache(maxsize=1)
def load_leaderboard() -> pd.DataFrame:
    """
    Load experiment_leaderboard_history.csv (full history, authoritative).
    Falls back to experiment_leaderboard.csv if history file is absent.
    Computes g4_drift inline if not already a column.
    """
    path = LEADERBOARD_HIST_CSV if LEADERBOARD_HIST_CSV.exists() else LEADERBOARD_CSV
    df = pd.read_csv(path)

    # Normalize column names — strip whitespace
    df.columns = [c.strip() for c in df.columns]

    # Compute G4 drift if not pre-computed by evaluate_sweep.py
    if "g4_drift" not in df.columns:
        if "val_acc" in df.columns and "test_acc" in df.columns:
            df["g4_drift"] = (df["val_acc"] - df["test_acc"]).abs()
        elif "val_actionable_accuracy" in df.columns and "test_actionable_accuracy" in df.columns:
            df["g4_drift"] = (
                df["val_actionable_accuracy"] - df["test_actionable_accuracy"]
            ).abs()

    return df


@lru_cache(maxsize=1)
def load_ensemble_config() -> dict:
    if not ENSEMBLE_CONFIG_JSON.exists():
        return {}
    return json.loads(ENSEMBLE_CONFIG_JSON.read_text())


def load_snapshot_for_label(run_label: str) -> pd.DataFrame | None:
    """
    On-demand: find the most recent snapshot CSV for a given run_label.
    Called only when the main leaderboard doesn't contain the label.
    """
    if not SNAPSHOTS_DIR.exists():
        return None
    matches = [
        f for f in SNAPSHOTS_DIR.glob("*.csv")
        if run_label.lower() in f.name.lower()
    ]
    if not matches:
        return None
    latest = sorted(matches, key=lambda f: f.name)[-1]
    df = pd.read_csv(latest)
    df.columns = [c.strip() for c in df.columns]
    return df


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def safe_row(row: dict) -> dict:
    """Replace NaN/inf so FastAPI's JSON serialization doesn't blow up."""
    return {
        k: (None if isinstance(v, float) and not math.isfinite(v) else v)
        for k, v in row.items()
    }


def ticker_col(df: pd.DataFrame) -> str | None:
    """Locate the ticker column regardless of exact name."""
    if "ticker" in df.columns:
        return "ticker"
    return next((c for c in df.columns if "ticker" in c.lower()), None)


def label_col(df: pd.DataFrame) -> str | None:
    """Locate the run_label column regardless of exact name."""
    if "run_label" in df.columns:
        return "run_label"
    return next((c for c in df.columns if "label" in c.lower()), None)