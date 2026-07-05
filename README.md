# Reinforcement Learning Trading Bot

Multi-seed RL ensemble for buy/sell signals on tech equities (NVDA, AMD, MU) using Binary PPO with walk-forward validation.

## Quick Start (5 minutes)

**Windows (PowerShell):**
```powershell
py -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
streamlit run src/dashboard/main.py
```

**macOS/Linux (Bash):**
```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
streamlit run src/dashboard/main.py
```

Dashboard opens at http://localhost:8501

## Current Status

| Ticker | Status | Seeds | Sharpe | Alpha |
|--------|--------|-------|--------|-------|
| NVDA | ✅ Promoted | [3, 13, 7, 42] | 2.03 | +0.11–+0.52 |
| AMD | ✅ Promoted | [13] | 2.01 | +0.28 |
| MU | ✅ Promoted | [3, 7, 42] | 1.77 | +3.07 |

See `CLAUDE.md` for setup, architecture, and workflows.

## Key Features

- **Multi-seed ensemble** — votes across 3+ models per ticker
- **Walk-forward validation** — train/val/test splits prevent look-ahead
- **6-gate promotion** — actionable accuracy, win rate, drift, trade rate
- **Exit manager** — configurable position exit rules
- **Streamlit dashboard** — signal analytics, experiments, performance metrics
- **Binary PPO** — discrete 2-action space (Buy, Hold)

## Common Commands

```bash
# Run dashboard
streamlit run src/dashboard/main.py

# Run experiment sweep
python src/experiments.py --ticker nvda --binary-actions --seeds 3,13 --timesteps 80000

# Evaluate sweep & promote
python scripts/evaluate_sweep.py --ticker NVDA --label nvda-exp10 --promote

# Test exit rules
python scripts/backtest_exit_rules.py --ticker amd --voting-method weighted

# Run tests
pytest tests/ -v
```

## Documentation

- **`CLAUDE.md`** — Development guide, setup, workflows, architecture
- **`context-map.md`** — Full system architecture and data flow
- **`PROJECT_STATE.md`** — Current phase, promotion status, next steps
