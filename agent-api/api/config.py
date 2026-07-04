from pathlib import Path

# agent-api/ always sits one level below repo root
REPO_ROOT = Path(__file__).resolve().parents[1]

LEADERBOARD_CSV      = REPO_ROOT / "data" / "experiment_leaderboard.csv"
LEADERBOARD_HIST_CSV = REPO_ROOT / "data" / "experiment_leaderboard_history.csv"
ENSEMBLE_CONFIG_JSON = REPO_ROOT / "staging" / "models" / "ensemble_config.json"
SNAPSHOTS_DIR        = REPO_ROOT / "data" / "experiment_snapshots"