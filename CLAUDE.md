# Claude Instructions for RL Stocks Trading Bot

**Project:** Reinforcement Learning Trading Bot (Multi-seed SAC/PPO Ensemble)  
**Last Updated:** 2026-07-04  
**Python Environment:** `.venv/` (use `.venv/Scripts/python` on Windows, `.venv/bin/python3` on macOS/Linux)

---

## Quick Project Summary

A sophisticated **multi-seed RL ensemble trading system** that generates buy/sell signals for tech equities (NVDA, AMD, MU, etc.) using:
- **Binary PPO** agents trained via Stable Baselines3
- **Walk-forward backtesting** with train/val/test splits
- **Streamlit dashboard** for signal analysis and experiment tuning
- **6-gate promotion framework** for model quality validation
- **Exit manager** for position management rules

**Current Status:** 3 tickers promoted (NVDA, AMD, MU). Infrastructure ready for MaskablePPO + action masking. Exit signal layer being wired to web dashboard.

---

## Development Setup

### Virtual Environment

```bash
# Windows PowerShell
py -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt

# macOS/Linux
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
```

### Configuration

Create `.env` in repo root for API keys:
```env
GEMINI_API_KEY=your_key_here
NEWS_SENTIMENT_PROVIDER=hybrid
OLLAMA_URL=http://127.0.0.1:11434/api/generate
```

### Running the Dashboard

```bash
# Main Signal Analytics dashboard
streamlit run src/dashboard/main.py

# With custom port
streamlit run src/dashboard/main.py --server.port 8502
```

---

## Core Architecture

### Directory Structure

```
src/
├── trading_env.py           # Gymnasium environment + PositionManager
├── experiments.py           # Main experiment runner (walk-forward, SAC/PPO)
├── ensemble.py              # Multi-seed ensemble inference (loads SparseEnsemble)
├── exit_manager.py          # Exit rules & position management
├── signal_analytics.py      # Signal metrics (Sharpe, accuracy, win rate)
├── market_data.py           # Yahoo Finance data + feature engineering
├── feature_engineering.py   # Technical indicators (RSI, MACD, ATR, etc.)
└── dashboard/               # Streamlit UI components
    ├── main.py              # Router + sidebar controls
    ├── config.py            # Paths, defaults, gates
    ├── model_utils.py       # Model discovery/loading
    ├── data_utils.py        # Market data loading, signal eval
    ├── pages/               # Page components
    │   ├── signal_analytics.py
    │   ├── experiments.py
    │   ├── experiment_insights.py
    │   └── performance_analytics.py
    └── components/          # Reusable UI widgets

staging/models/
├── ensemble_config.json     # *** CANONICAL ensemble seed config ***
├── nvda/                    # Ticker subdirs
├── amd/
└── mu/

data/
├── tech_training_data.csv                # Market data + features
├── experiment_leaderboard.csv            # Main results leaderboard
├── experiment_summary.json               # Experiment metadata
├── dashboard_signals/                    # Exported signals for web dashboard
│   ├── nvda_signals.json
│   ├── amd_signals.json
│   └── mu_signals.json
└── audit/                                # Exit backtest reports

tests/
├── test_ensemble.py                      # Ensemble loading/inference
├── test_exit_manager.py                  # Exit logic verification
├── test_signal_alignment.py              # No look-ahead verification
└── ...

scripts/
├── backtest_exit_rules.py                # ExitManager ablation runner
├── evaluate_sweep.py                     # Post-experiment evaluation + gates
├── export_signals_for_dashboard.py       # Signal export script
└── analyze_reward_divergence.py          # Diagnostic analysis
```

### Key Files & Entry Points

| File | Purpose |
|------|---------|
| `src/dashboard/main.py` | Dashboard entry point (page router, sidebar) |
| `src/experiments.py` | Training orchestrator (walk-forward, SAC/PPO, gates) |
| `src/ensemble.py` | Multi-seed voting/averaging inference |
| `staging/models/ensemble_config.json` | **Single source of truth** for production ensembles |
| `src/exit_manager.py` | Exit rule logic (trailing stop, profit take, etc.) |
| `src/signal_analytics.py` | Signal quality metrics computation |
| `src/trading_env.py` | Gymnasium env + PositionManager (P&L tracking) |
| `data/experiment_leaderboard.csv` | All model results + metrics |

---

## Critical Concepts

### Promoted Tickers (Phase 2B — Binary PPO)

| Ticker | Status | Seeds | Min Hold | Trade Rate | Sharpe | Alpha |
|--------|--------|-------|----------|-----------|--------|-------|
| **NVDA** | ✅ Promoted | [3, 13, 7, 42] | 1 bar | 48–62% | 2.03 | +0.11–+0.52 |
| **AMD** | ✅ Promoted | [13] | 3 bars | 42.9% | 2.01 | +0.28 |
| **MU** | ✅ Promoted | [3, 7, 42] | 1 bar | 95.6% ⚠️ | 1.77 | +3.07 |

**Key Findings:**
- Min-hold constraint is **ticker-specific**. NVDA requires `min_hold_bars=1`; AMD/MU work at 3.
- Feature space (raw vs stationary) is **per-ticker** in `ensemble_config.json`.
- NVDA uses raw 10-feature space; AMD/MU use stationary 27-feature space.
- Binary PPO + discrete action masking is the "gold standard" for these mega-caps.

### Ensemble Configuration (staging/models/ensemble_config.json)

**Structure:**
```json
{
  "nvda": {
    "active_seeds": [3, 13, 7, 42],
    "ensemble_method": "voting",
    "run_label": "nvda-ppo-minhold1-extended",
    "leaderboard_csv": "data/experiment_leaderboard.csv",
    "min_hold_bars": 1,
    "use_stationary_features": false,
    "use_cooldown_obs": false,
    "production_ready": true
  },
  "amd": { ... },
  "mu": { ... }
}
```

This is **manually maintained** and the canonical source for production models.

### 6-Gate Promotion Framework

| Gate | Metric | Threshold | Notes |
|------|--------|-----------|-------|
| 1 | Test actionable accuracy | ≥ 0.525 | Lowered for Binary PPO |
| 2 | Test trade win rate | ≥ 0.50 | Lowered for Binary PPO |
| 3 | Test alpha vs QQQ | ≥ 0.0005 | Tightened for alpha-first |
| 4 | \|Val accuracy - Test accuracy\| | ≤ 0.05 | Generalization gap |
| 5 | Test return CV by config | < 0.50 | Tightened for PPO stability |
| 6 | Test trade rate | ∈ [0.40, 0.80] | Gate 6 waiver possible for high-momentum sectors |

**Gate 6 Waiver** can be granted if Gates 1–5 pass + trade_win_rate ≥ 0.54 + penalty tuning unresponsive + ticker in documented bull cycle (e.g., semiconductor upcycle for MU).

---

## Common Workflows

### 1. Run an Experiment Sweep

```bash
# Full sweep (walk-forward validation)
python src/experiments.py --ticker nvda --seeds 3,13,7,42 --binary-actions --timesteps 80000 \
  --reward-hold-penalty-scale 0.01 --min-hold-bars 1 --run-label nvda-exp10

# Fast smoke test (2 seeds, 2k timesteps)
python src/experiments.py --ticker nvda --seeds 3,13 --binary-actions --timesteps 2000 --max-runs 2

# With stationary features (AMD/MU)
python src/experiments.py --ticker amd --seeds 13,21,7,42 --binary-actions --use-stationary-features \
  --min-hold-bars 3 --timesteps 60000 --run-label amd-masked-ppo-v1
```

### 2. Evaluate & Promote a Sweep

```bash
# Evaluate a completed sweep against 6 gates
python scripts/evaluate_sweep.py --leaderboard data/experiment_leaderboard.csv \
  --ticker AMD --label amd-masked-ppo-v1 --promote

# Promote manually (update ensemble_config.json)
# Edit: staging/models/ensemble_config.json → add/update "amd" entry with new seeds
```

### 3. Tune Signals via Dashboard

```bash
# Open dashboard
streamlit run src/dashboard/main.py

# Workflow:
# 1. Select "Signal Analytics" page
# 2. Pick ticker (NVDA, AMD, MU, etc.)
# 3. Enable "Use Ensemble" toggle
# 4. Adjust threshold, horizon, min_hold_bars
# 5. Click "Run Analytics" → view Sharpe, win rate, confusion matrix
# 6. Inspect individual seed performance
```

### 4. Test Exit Rules (ExitManager)

```bash
# Full val sweep + test evaluation
python scripts/backtest_exit_rules.py --ticker nvda

# Test-only for a specific config
python scripts/backtest_exit_rules.py --ticker nvda --config profit_take_2pct --test-only

# Weighted voting ensemble
python scripts/backtest_exit_rules.py --ticker amd --voting-method weighted
```

Output: `data/audit/exit_backtest/backtest_summary.md`

### 5. Run Tests

```bash
# All tests
pytest tests/ -v

# Specific test
pytest tests/test_ensemble.py -v

# Test without captured output
pytest tests/test_ensemble.py -v -s
```

---

## Data Pipeline

### Market Data Loading

```python
from src.market_data import get_tech_training_data

# Load daily OHLCV + features
df = get_tech_training_data(
    include_news=True,           # Add sentiment features
    use_stationary_features=True # Log returns, normalized indicators
)

# Structure:
# Columns: Date, Open, High, Low, Close, Volume, RSI, MACD, ATR, ...
# Also: train/val/test split labels in 'split' column
```

### Feature Engineering

- **Raw features:** Open, High, Low, Close, Volume
- **Technical indicators:** RSI, MACD, Bollinger Bands, ATR, SMA 20/50
- **Stationary features:** Log returns, normalized indicators (for AMD/MU)
- **News sentiment:** Optional daily sentiment aggregation (TBD)

---

## Testing & Verification

### Run Smoke Tests

```bash
# Quick integration test
python tests/test_script.py

# Full test suite
pytest tests/ -v
```

### Critical Test Areas

1. **No look-ahead leakage** — test data never sees future prices
2. **Ensemble loading** — seeds load correctly from leaderboard
3. **Exit manager logic** — exit rules fire correctly
4. **Reward calculation** — no future data in reward shaping
5. **Weight delta capping** — position sizing respects constraints

---

## Exit Signal Phase 3 (In Progress)

**Decision (current):**
- **NVDA:** `no_exit` by default
- **AMD:** `trailing_5pct`
- **MU:** `trailing_3pct`

**Next Steps:**
1. Lock signal contract: `{date, action, confidence, exit_fired, exit_rule}`
2. Implement `/api/signals/:symbol` endpoint in web dashboard backend
3. Wire exit overlays in `TradingChart.jsx`
4. Add `ExitControls.jsx` for rule selection
5. End-to-end validation (backend + frontend)

See `PROJECT_STATE.md` Section 9 for detailed acceptance criteria.

---

## Common Issues & Diagnostics

### Issue: Model not found in leaderboard

**Cause:** Leaderboard path mismatch or stale model references.

**Solution:**
```bash
# Verify leaderboard exists
ls -la data/experiment_leaderboard.csv

# Check ensemble config paths
python -c "import json; print(json.load(open('staging/models/ensemble_config.json', 'r')))"

# Regenerate leaderboard (slow)
python scripts/evaluate_sweep.py --root-dir .
```

### Issue: Dashboard shows 0% trade rate

**Cause:** Policy collapsed to cash; likely due to strict transaction costs or aggressive hold penalties.

**Solution:**
```bash
# Run with low-friction preset
python src/experiments.py --ticker <t> --reward-ignore-transaction-cost \
  --reward-turnover-penalty-scale 0.00 --reward-action-bonus-scale 0.02
```

### Issue: Large val/test accuracy gap (> 0.05)

**Cause:** Overfitting or regime shift between validation and test periods.

**Diagnosis:**
```bash
# Inspect individual seed drifts
python scripts/analyze_reward_divergence.py --plot
# → data/audit/divergence_dashboard.png
```

---

## Performance Tuning & Ablations

### Reward Shaping Knobs

Available in `experiments.py --reward-*` flags:

```python
--reward-mode                    # "legacy", "sharpe", "sortino"
--reward-hold-penalty-scale      # Penalty for Hold actions (default 0.01)
--reward-turnover-penalty-scale  # Penalty for frequent trading (default 0.01)
--reward-action-bonus-scale      # Bonus for action diversity (default 0.02)
--reward-ignore-transaction-cost # Exclude fees in reward (default False)
--reward-return-scale            # Weight on portfolio return (default 1.0)
--reward-direction-scale         # Weight on directional alignment (default 1.0)
--reward-clip                    # Symmetric reward clipping (default 10.0)
```

### Architecture Flags

```python
--binary-actions                 # Use Binary PPO (2 actions: Buy, Hold)
--use-stationary-features        # Log returns + normalized indicators
--use-cooldown-obs               # Include cooldown counter in observation
--use-action-masking             # sb3_contrib.MaskablePPO
--min-hold-bars N                # Minimum hold period (1 or 3)
```

---

## Key Dependencies

| Package | Version | Purpose |
|---------|---------|---------|
| stable-baselines3 | 2.x | SAC/PPO algorithms |
| gymnasium | 0.29+ | RL environment (replaces gym) |
| sb3-contrib | 2.x | MaskablePPO for action masking |
| pandas | 2.x | Data manipulation |
| numpy | 1.x | Numerical computing |
| torch | 2.x | PyTorch backend for SB3 |
| streamlit | 1.28+ | Dashboard UI |
| yfinance | Latest | Yahoo Finance data |
| scikit-learn | Latest | Signal metrics (confusion matrix, etc.) |

---

## Critical Files to Protect

| File | Why | Fallback |
|------|-----|----------|
| `staging/models/ensemble_config.json` | Canonical ensemble config | Manual re-entry (data loss) |
| `data/experiment_leaderboard.csv` | All model results | Regenerate via experiments (slow) |
| `data/experiment_snapshots/` | Training snapshots for replay | Recompute experiments |
| `.venv/` | Environment with deps | `pip install -r requirements.txt` |

---

## Common Commands Reference

```bash
# Setup
py -m venv .venv && .venv\Scripts\Activate.ps1 && pip install -r requirements.txt

# Dashboard
streamlit run src/dashboard/main.py --server.port 8501

# Experiments
python src/experiments.py --ticker nvda --binary-actions --seeds 3,13 --timesteps 80000

# Evaluation
python scripts/evaluate_sweep.py --ticker NVDA --label nvda-exp10 --promote

# Exit testing
python scripts/backtest_exit_rules.py --ticker amd --voting-method weighted

# Tests
pytest tests/ -v

# Export signals
python scripts/export_signals_for_dashboard.py
```

---

## References & Documentation

- **`context-map.md`** — Full architecture, data flow, dependencies
- **`PROJECT_STATE.md`** — Current status, promoted tickers, phase 3 plans
- **`README.md`** — Quick start guide, feature overview
- **`EXIT_SIGNAL_TODO.md`** — Phase 3 exit signal tasks
- **`REFINEMENT_TODO.md`** — Tuning & refinement work items
- **`docs/TRADING_DASHBOARD_WIRING.md`** — Web dashboard integration guide

---

## Session Notes

**For the next Claude session:**
- Check `PROJECT_STATE.md` first for current promotion status
- Verify `.venv` is active before running any Python scripts
- Always confirm model paths in `staging/models/ensemble_config.json` match leaderboard
- Use `pytest tests/ -v` before committing changes to verify no regressions
- When adding new features, test on a single seed before full sweep

