# quant-experiment-agent API

Structured lookup layer for the Binary PPO trading experiment history.
Called by the `quant-experiment-agent` Foundry agent instead of doing
vector retrieval over structured CSV/JSON data.

## Setup

```bash
# From repo root
cd agent-api/
python -m venv .venv

# Mac / Linux / Pi
source .venv/bin/activate

# Windows
.venv\Scripts\Activate.ps1

pip install -r requirements.txt
```

## Run

```bash
# From agent-api/
uvicorn main:app --reload --port 8001
```

API docs auto-generated at: http://localhost:8001/docs

## Endpoints

| Method | Path | Description |
|--------|------|-------------|
| GET | `/health` | Liveness + leaderboard row count + column list |
| GET | `/runs/{ticker}` | All runs for a ticker. Optional `?run_label=` filter |
| GET | `/runs/label/{run_label}` | Rows for a specific run_label, snapshot fallback |
| GET | `/gates` | List all gates and what they measure |
| GET | `/gates/{gate_name}/failures` | Cross-ticker failure report. Optional `?ticker=` `?run_label=` |
| GET | `/gates/{gate_name}/summary` | Per-ticker pass rate for a gate |
| GET | `/ensemble/config` | Full ensemble_config.json |
| GET | `/ensemble/config/{ticker}` | Ensemble config for one ticker |
| POST | `/cache/invalidate` | Reload leaderboard + config from disk |

Gate names: `g1` `g2` `g3` `g4` `g5` `g6`

## First run checklist

1. Hit `/health` — verify `leaderboard_columns` includes the column names
   your gate thresholds depend on (`clean_cv`, `test_alpha_vs_qqq`, etc.)
2. If columns differ from what `gates.py` expects, update the column names
   in `gates.py` THRESHOLDS to match — do not rename the CSV columns.
3. `/cache/invalidate` after any restage or ensemble config update.

## Notes

- `data/experiment_leaderboard_history.csv` is loaded once and cached.
  The 1026 snapshot CSVs are never bulk-loaded — only fetched on-demand
  when a `run_label` query misses the main leaderboard.
- `agent-api/.venv/` is isolated from the repo root `.venv` (SB3/torch stack).
  Keep them separate.
- CORS is open (`*`) for local dev. Tighten `allow_origins` in `main.py`
  before exposing beyond localhost or the Pi LAN.