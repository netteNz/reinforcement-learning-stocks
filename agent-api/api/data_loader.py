# data_loader.py
import pandas as pd
from functools import lru_cache
from config import LEADERBOARD_CSV, LEADERBOARD_HIST_CSV, SNAPSHOTS_DIR, ENSEMBLE_CONFIG_JSON
import json

# Gate column mapping — must stay in sync with evaluate_sweep.py
GATE_COLUMNS = {
    "g1": "test_actionable_accuracy",
    "g2": "test_trade_win_rate",
    "g3": "test_alpha_vs_qqq",
    "g4_drift": None,          # computed: abs(val_acc - test_acc)
    "g5": "clean_cv",
    "g6": "test_trade_rate",
}

@lru_cache(maxsize=1)
def load_leaderboard() -> pd.DataFrame:
    df = pd.read_csv(LEADERBOARD_HIST_CSV)
    # Compute G4 drift inline if not already a column
    if "g4_drift" not in df.columns and "val_acc" in df.columns:
        df["g4_drift"] = (df["val_acc"] - df["test_acc"]).abs()
    return df

@lru_cache(maxsize=1)
def load_ensemble_config() -> dict:
    return json.loads(ENSEMBLE_CONFIG_JSON.read_text())

def load_snapshot_for_label(run_label: str) -> pd.DataFrame | None:
    """On-demand load of a specific run's snapshot CSV from experiment_snapshots/."""
    matches = list(SNAPSHOTS_DIR.glob(f"*{run_label}*.csv"))
    if not matches:
        return None
    # Most recent file wins
    return pd.read_csv(sorted(matches)[-1])