# Reinforcement Learning Stocks - Full Context Map

## Project Overview

A sophisticated reinforcement learning trading system for multi-ticker equity analysis, featuring:
- **Multi-seed SAC/PPO ensemble** for buy/sell signal generation
- **Walk-forward backtesting** with proper train/val/test splits
- **Streamlit dashboard** for signal analytics and experiment visualization
- **Exit manager** for intelligent position management
- **Stage 1 & Stage 2** experiment workflows with 6-gate promotion framework

**Root Directory:** `D:\code\agentic-development\reinforcement-learning-stocks`

---

## Directory Structure & Purpose

```
reinforcement-learning-stocks/
├── src/                          # Core application code
│   ├── __init__.py
│   ├── trading_env.py            # Gymnasium trading environment (PositionManager, TradingEnv)
│   ├── trading_agent.py          # Base agent interface
│   ├── ensemble.py               # SparseEnsemble & EnsembleAgent (multi-seed inference)
│   ├── exit_manager.py           # Position exit logic and decision rules
│   ├── experiments.py            # Experiment runner (walk-forward, SAC/PPO training, gates)
│   ├── signal_analytics.py       # Signal quality metrics (Sharpe, win rate, actionability)
│   ├── market_data.py            # Yahoo Finance data loading, feature engineering
│   ├── feature_engineering.py    # Technical indicators (RSI, MACD, Bollinger Bands, etc.)
│   ├── news_data.py              # News sentiment integration
│   ├── train_bot.py              # Training orchestration
│   ├── baseline_agents.py        # Buy-hold, supervised baseline comparisons
│   ├── supervised_baseline.py    # Supervised learning baseline
│   ├── quant_report.py           # Quantitative analysis reporting
│   ├── rolling_window_validation.py # Validation methodology
│   ├── stage2_h*.py              # Stage 2 hypothesis runners (h1, h2, h3, h4)
│   ├── buyhold_benchmark.py      # Buy & hold benchmark comparison
│   │
│   └── dashboard/                # Streamlit analytics dashboard
│       ├── __init__.py
│       ├── main.py               # Entry point: page router, sidebar controls, model discovery
│       ├── config.py             # Paths, defaults, promotion gates
│       ├── model_utils.py        # Model discovery, loading, curation
│       ├── data_utils.py         # Market data loading, signal evaluation
│       ├── leaderboard.py        # Leaderboard parsing & ticker detection
│       ├── analytics.py          # PnL, action mix calculations
│       ├── pages/                # Dashboard page components
│       │   ├── __init__.py
│       │   ├── signal_analytics.py      # Main signal evaluation page
│       │   ├── experiments.py           # Experiment runner page
│       │   ├── experiment_insights.py   # Experiment analytics page
│       │   └── performance_analytics.py # Performance charts & metrics
│       └── components/           # Reusable UI components
│           ├── __init__.py
│           ├── metrics.py        # Metric cards, confusion matrix, headroom
│           ├── charts.py         # Altair price/signal charts, ROC curves
│           ├── ensemble.py       # Ensemble config display
│           └── gates.py          # Promotion gate display
│
├── staging/                      # Production model staging area
│   ├── models/
│   │   ├── ensemble_config.json  # *** Canonical ensemble seed config ***
│   │   ├── nvda/, aapl/, amd/... # Ticker-specific model subdirs
│   │   └── {seed}/               # Seed folders with .zip model files
│   └── src/                      # Experimental staging code
│
├── models/                       # Development model snapshots
│   └── {snapshot_dir}/
│
├── data/                         # Data artifacts & results
│   ├── tech_training_data.{csv,parquet}  # Feature-engineered market data
│   ├── tech_training_data_stationary.parquet
│   ├── experiment_leaderboard.csv        # Main leaderboard (1d interval)
│   ├── experiment_leaderboard_intraday_5m.csv
│   ├── experiment_reward_leaderboard.csv # Reward metrics
│   ├── experiment_summary.json
│   ├── experiment_snapshots/
│   │   ├── intraday_5m/           # 5-minute interval snapshots
│   │   ├── intraday_5m_batch_a/
│   │   └── ...
│   ├── dashboard_signals/        # *** Exported ensemble signals (for trading-dashboard) ***
│   │   ├── nvda_signals.json
│   │   ├── aapl_signals.json
│   │   └── ...
│   ├── exp_1_nvda_10seed_foundation_snapshots/
│   ├── exp_2_aapl_10seed_foundation_snapshots/
│   ├── exp_3_amd_10seed_foundation_snapshots/
│   └── audit/                    # Audit reports
│       ├── exit_backtest/
│       └── exit_signal_sweep/
│
├── results/                      # Experiment result sets
│   ├── stage1/
│   ├── stage1_confirmation_3seed/
│   ├── stage1_rolling_window/
│   ├── stage1_step5-11/
│   ├── stage1_step*/
│   └── stage2_h{1,2,3,4}/
│
├── tests/                        # Test suite
│   ├── test_ensemble.py          # Ensemble loading & inference
│   ├── test_exit_manager.py      # Exit logic verification
│   ├── test_experiments_integration.py
│   ├── test_reward_no_lookahead.py
│   ├── test_signal_alignment.py
│   ├── test_weight_delta_cap.py
│   ├── test_e2e_reward_fix.py
│   ├── test_mps_acceleration.py
│   └── test_event_research_pipeline.py
│
├── docs/                         # Documentation
│   ├── TRADING_DASHBOARD_WIRING.md  # *** Dashboard integration guide ***
│   ├── TRADING_DASHBOARD_INTEGRATION.md
│   ├── PLAN.md
│   ├── EXECUTION_PROCESS.md
│   ├── STAGE1_REGIME_SHIFT_REPORT.md
│   ├── STAGE1_EXIT_REPORT.md
│   ├── AAPL_LEAKAGE_AUDIT.md
│   ├── ENVIRONMENT_REALISM_AUDIT_2026_04_02.md
│   └── ...
│
├── scripts/                      # Utility scripts
│   ├── archive/
│   ├── research/
│   └── export_signals_for_dashboard.py (optional)
│
├── .github/                      # GitHub workflows & custom skills
│   └── skills/
│       ├── backtest-auditor/
│       ├── signal-analytics-interpreter/
│       ├── signal-dashboard-troubleshooter/
│       ├── strategy-refinement-analyst/
│       ├── reward-architect/
│       └── ...
│
├── notebooks/                    # Jupyter notebooks (research, exploration)
├── event-research/               # Event-driven research pipeline
├── scratch/                      # Scratch/temporary work
├── logs/                         # Experiment logs
├── archives/                     # Historical data
├── reports/                      # Generated reports
│
├── .venv/                        # Python virtual environment
├── .venv-wsl/                    # WSL virtual environment
├── .claude/                      # Claude Code project config
├── .vscode/                      # VS Code settings
├── .github/                      # GitHub Actions & CI
│
├── pyproject.toml (or requirements.txt)
├── .gitignore
└── README.md
```

---

## Core Modules & Dependencies

### 1. **Environment & Market Data**

| Module | Purpose | Key Functions | Dependencies |
|--------|---------|---------------|--------------|
| `market_data.py` | Yahoo Finance data loading, feature engineering | `get_tech_training_data()`, `fetch_yahoo_ohlcv()`, `interval_slug()`, `normalize_interval_key()` | pandas, yfinance, TICKER_PRESETS |
| `feature_engineering.py` | Technical indicators (RSI, MACD, Bollinger, etc.) | Feature calculation pipeline | pandas, numpy |
| `trading_env.py` | Gymnasium trading environment | `TradingEnv` class, `PositionManager` | gymnasium, numpy |
| `news_data.py` | Sentiment integration (optional) | News data ingestion | pandas |

### 2. **Model Training & Inference**

| Module | Purpose | Key Functions | Dependencies |
|--------|---------|---------------|--------------|
| `trading_agent.py` | Base agent interface | Agent abstraction | stable_baselines3 |
| `experiments.py` | Main experiment orchestrator | `run_experiment()`, walk-forward logic, SAC/PPO training | stable_baselines3, torch, pandas |
| `ensemble.py` | Multi-seed ensemble inference | `SparseEnsemble`, `EnsembleAgent`, `load_top_n_models()` | pandas, numpy, stable_baselines3 |
| `signal_analytics.py` | Signal quality metrics | `compute_metrics()`, `confusion_matrix()`, `enrich_with_truth_labels()` | pandas, numpy, sklearn |
| `exit_manager.py` | Position exit logic | Exit decision rules | pandas, numpy |

### 3. **Dashboard (Streamlit UI)**

| Module | Purpose | Key Functions | Dependencies |
|--------|---------|---------------|--------------|
| `dashboard/main.py` | **Entry point & router** | `main()` - sidebar, page selection, model discovery | streamlit, config |
| `dashboard/config.py` | **Global paths & defaults** | Leaderboard paths, promotion gates, thresholds | pathlib |
| `dashboard/model_utils.py` | Model discovery & loading | `_list_available_models()`, `_load_model()`, `_curate_model_choices()` | pathlib, zipfile, pickle |
| `dashboard/data_utils.py` | Market data loading, signal eval | `load_market_data()`, `evaluate_signals()` | pandas, pathlib |
| `dashboard/leaderboard.py` | Leaderboard parsing | `_detect_leaderboard_tickers()` | pandas |
| `dashboard/analytics.py` | PnL & action tables | `add_cumulative_pnl()`, `build_action_mix_table()` | pandas, numpy |
| `dashboard/pages/signal_analytics.py` | **Main analytics page** | `render_signal_analytics_page()` - model eval, ensemble toggle | streamlit, altair |
| `dashboard/pages/experiments.py` | Experiment runner page | `render_experiments_page()` | streamlit, experiments |
| `dashboard/pages/experiment_insights.py` | Experiment insights | `render_experiment_insights_page()` | streamlit, pandas |
| `dashboard/pages/performance_analytics.py` | Performance metrics | `render_performance_analytics_page()` | streamlit, altair |
| `dashboard/components/metrics.py` | Metric cards, confusion matrix | `render_metrics()`, `render_confusion_heatmap()` | streamlit, pandas |
| `dashboard/components/charts.py` | Price/signal charts, ROC | `render_charts()`, `render_roc_curves()` | altair, pandas |
| `dashboard/components/ensemble.py` | Ensemble config display | `display_ensemble_config()` | streamlit, json |
| `dashboard/components/gates.py` | Promotion gates display | Gate evaluation visualization | streamlit |

### 4. **Experiment Runners**

| Module | Purpose |
|--------|---------|
| `train_bot.py` | Training orchestration |
| `baseline_agents.py` | Buy-hold and supervised baselines |
| `supervised_baseline.py` | Supervised ML baseline |
| `stage2_h1_runner.py`, `stage2_h2_runner.py`, etc. | Stage 2 hypothesis-specific runners |
| `buyhold_benchmark.py` | Buy & hold benchmark |
| `rolling_window_validation.py` | Walk-forward validation |
| `quant_report.py` | Quantitative analysis reports |

---

## Data Flow & Architecture

### A. **Training Pipeline** (experiments.py)

```
market_data.py (get_tech_training_data)
    ↓
feature_engineering.py (calculate indicators)
    ↓
trading_env.py (TradingEnv instantiation)
    ↓
experiments.py (walk-forward split)
    ├─ Train: SAC/PPO.learn() on training subset
    ├─ Val: evaluate on validation subset
    └─ Test: deterministic inference on test subset
    ↓
signal_analytics.py (compute_metrics, confusion_matrix)
    ↓
leaderboard.csv (export results)
```

### B. **Dashboard Pipeline** (Streamlit UI)

```
dashboard/main.py (page router & sidebar)
    ├─ Model Discovery → model_utils.py (_list_available_models)
    ├─ Leaderboard Detection → leaderboard.py (_detect_leaderboard_tickers)
    └─ Session State → ticker, model_path, interval, data_path
    
SIGNAL ANALYTICS PAGE:
    render_signal_analytics_page()
    ├─ data_utils.py (load_market_data) ←─ data/tech_training_data.{csv,parquet}
    ├─ model_utils.py (_load_model) ←─ models/ or staging/models/
    ├─ signal_analytics.py (evaluate_signals)
    │   └─ ensemble.py (SparseEnsemble) ←─ staging/models/ensemble_config.json
    ├─ analytics.py (add_cumulative_pnl, build_action_mix_table)
    ├─ components/charts.py (render_charts, render_roc_curves) ← altair
    ├─ components/metrics.py (render_metrics, confusion_heatmap)
    └─ components/ensemble.py (display_ensemble_config)

EXPERIMENTS PAGE:
    render_experiments_page()
    ├─ experiments.py (run_experiment) ← triggers training
    └─ leaderboard reading
    
EXPERIMENT INSIGHTS PAGE:
    render_experiment_insights_page()
    └─ Results analysis
    
PERFORMANCE ANALYTICS PAGE:
    render_performance_analytics_page()
    └─ Historical performance charts
```

### C. **Ensemble Inference Path**

```
staging/models/ensemble_config.json (seed definitions)
    ↓
ensemble.py (SparseEnsemble)
    ├─ from_config(path, ticker) → loads leaderboard_csv
    ├─ filter_active_seeds(min_test_trades) → removes collapsed seeds
    ├─ load_top_n_models(n=3) → loads .zip model files
    └─ run_inference(data) → voting or averaging across seeds
    
Data Input: market data (OHLCV + features)
    ↓
Individual model outputs → action probabilities or discrete actions
    ↓
Voting/Averaging aggregation
    ↓
Output: buy/sell signals with confidence
```

---

## Ensemble Configuration (staging/models/ensemble_config.json)

**Purpose:** Single source of truth for production-ready ensemble seeds per ticker.

**Structure:**
```json
{
  "nvda": {
    "active_seeds": [3, 13, 7, 42],        // List of seed IDs to include
    "ensemble_method": "voting",            // "voting" or "averaging"
    "top_3_mean_sharpe": 1.86,             // Metadata: mean Sharpe of top 3
    "top_3_mean_val_test_gap": 0.007,      // Metadata: generalization gap
    "production_ready": true,               // Boolean or "monitor"
    "notes": "...",                         // Human notes
    "run_label": "nvda-ppo-minhold1-extended",  // Experiment label
    "leaderboard_csv": "path/to/leaderboard.csv",
    "min_hold_bars": 1,                     // Optional: minimum hold period
    "use_stationary_features": false,       // Optional: feature flags
    "use_cooldown_obs": false               // Optional: cooldown obs
  },
  ...
}
```

**How it's used:**
1. Dashboard reads it when "Use Ensemble" toggle is enabled
2. `SparseEnsemble.from_config()` loads the specified seeds
3. Models are loaded from `staging/models/{ticker}/{seed}/*.zip`
4. Inference aggregates votes/means across seeds

---

## Dashboard Wiring (Streamlit → Ensemble → Signals)

### Signal Analytics Page Flow

```
1. SIDEBAR CONTROLS (dashboard/main.py)
   ├─ Page selection radio → determines which page renders
   ├─ Ticker dropdown → TICKER_PRESETS keys
   ├─ Model/Data interval selection → auto-detect vs manual
   ├─ Model selector → _list_available_models() + _curate_model_choices()
   ├─ Data CSV path → load_market_data()
   └─ Threshold, horizon, deterministic_policy, min_hold_bars

2. ENTER SIGNAL ANALYTICS PAGE (pages/signal_analytics.py)
   ├─ Simulation Controls
   │   ├─ "Use Ensemble" toggle (True/False)
   │   └─ "Binary Actions (SAC)" checkbox (if single model)
   ├─ Data Split selector (Train/Val/Test/Full)
   ├─ Min Hold Bars (ticker-specific defaults)
   └─ Run Button → execute render_signal_analytics_page()

3. LOAD DATA & MODELS
   ├─ data_utils.load_market_data(data_path)
   │   └─ Returns: DataFrame with OHLCV + features + split labels
   ├─ IF use_ensemble:
   │   └─ ensemble.py (SparseEnsemble)
   │       ├─ from_config('staging/models/ensemble_config.json', ticker)
   │       ├─ filter_active_seeds()
   │       ├─ load_top_n_models(n=3)
   │       └─ run_inference(data) → signals
   └─ ELSE:
       └─ model_utils._load_model(model_path)
           └─ Returns: SAC/PPO agent

4. EVALUATE SIGNALS
   ├─ data_utils.evaluate_signals(...)
   │   ├─ Forward-move truth labels (threshold, horizon)
   │   ├─ Action generation from model output
   │   └─ Signal metrics (accuracy, actionability, win rate)
   └─ signal_analytics.compute_metrics()
       ├─ Sharpe ratio, sortino, calmar
       ├─ Win rate, profit factor
       └─ Confusion matrix

5. RENDER DASHBOARD COMPONENTS
   ├─ components/metrics.py (render_metrics)
   │   ├─ Metric cards (Sharpe, win rate, etc.)
   │   ├─ Confusion heatmap
   │   └─ Theoretical headroom
   ├─ components/charts.py (render_charts, render_roc_curves)
   │   ├─ Price + signal overlay (Altair)
   │   └─ ROC curves per class
   ├─ components/ensemble.py (display_ensemble_config)
   │   └─ Show active seeds, method, production status
   └─ analytics.py (build_action_mix_table, add_cumulative_pnl)
       ├─ Action distribution table
       └─ Cumulative PnL chart
```

### Key Session State Variables

Stored in `st.session_state` to persist across Streamlit reruns:

| Key | Type | Purpose |
|-----|------|---------|
| `signal_dashboard_model_path` | str | Selected model file path |
| `signal_dashboard_model_interval` | str | "5m" or "1d" |
| `signal_dashboard_data_path` | str | Selected data CSV path |
| `signal_dashboard_interval_mode` | str | "Auto", "5m", or "1d" |
| `signal_dashboard_model_last_ticker` | str | Previous ticker (to detect change) |
| `signal_dashboard_last_ticker` | str | Previous ticker for data path |
| `signal_dashboard_last_interval` | str | Previous interval (to detect change) |

---

## Testing Strategy

| Test File | Scope | What it Tests |
|-----------|-------|---------------|
| `test_ensemble.py` | Ensemble loading & inference | `SparseEnsemble` load/rank/infer logic |
| `test_exit_manager.py` | Exit decision logic | Exit rules, position management |
| `test_signal_alignment.py` | Signal integrity | Forward-move truth labels, no look-ahead |
| `test_reward_no_lookahead.py` | Reward calculation | Verify no future data leakage |
| `test_weight_delta_cap.py` | Weight deltas | Verify position sizing limits |
| `test_experiments_integration.py` | End-to-end experiments | Full pipeline correctness |
| `test_e2e_reward_fix.py` | Reward system | Reward fix verification |
| `test_mps_acceleration.py` | GPU acceleration | MPS (Apple Silicon) compatibility |
| `test_event_research_pipeline.py` | Event research | Event data pipeline |

---

## Trading Dashboard Integration (External)

**Location:** `../trading-dashboard` (sister repo)

**Wiring Strategy:** See `docs/TRADING_DASHBOARD_WIRING.md`

### Approach A: Exported Signals (Recommended)

```
This repo (RL):
  1. Export ensemble signals → data/dashboard_signals/{ticker}_signals.json
  2. Script: scripts/export_signals_for_dashboard.py

Trading Dashboard (external):
  1. Add route: /api/signals/<symbol>
  2. Read from: ../reinforcement-learning-stocks/data/dashboard_signals/
  3. Frontend: import ExitControls component
  4. Display: signal confidence, entry/exit recommendations
```

**File locations for integration:**
- RL Repo: `data/dashboard_signals/nvda_signals.json` (exported)
- Dashboard Backend: `backend/app.py` (add route)
- Dashboard Frontend: `frontend/src/components/ExitControls.jsx`

### Approach B: Integrated (Optional)

```
Dashboard imports RL repo directly:
  - pip install -e ../reinforcement-learning-stocks
  - Blueprint for /api/signals using ensemble.py
  - More powerful but requires dependency alignment
```

---

## Key Entry Points

### Running the Dashboard

```bash
# Activate venv
.venv\Scripts\activate

# Run Streamlit UI
streamlit run src/dashboard/main.py

# Or with host/port
streamlit run src/dashboard/main.py --server.port 8501 --server.address 0.0.0.0
```

### Running Experiments

```bash
# Full experiment sweep
python -m src.experiments --ticker NVDA --interval 1d

# Stage 2 hypothesis runners
python -m src.stage2_h1_runner
python -m src.stage2_h2_runner
python -m src.stage2_h3_runner
python -m src.stage2_h4_runner
```

### Exporting Signals for Dashboard

```bash
# Export ensemble signals
python scripts/export_signals_for_dashboard.py
# Creates: data/dashboard_signals/{ticker}_signals.json
```

### Running Tests

```bash
# All tests
pytest tests/

# Specific test
pytest tests/test_ensemble.py -v
```

---

## Configuration & Constants

### Dashboard Defaults (dashboard/config.py)

```python
DEFAULT_TICKER = "nvda"
DEFAULT_DATA_PATH = Path("data/tech_training_data.parquet")
DEFAULT_LEADERBOARD_PATH = Path("data/experiment_leaderboard.csv")
INTRADAY_5M_LEADERBOARD_PATH = Path("data/experiment_leaderboard_intraday_5m.csv")

RECOMMENDED_THRESHOLD = 0.0020       # Forward-move threshold
RECOMMENDED_HORIZON = 1              # Bars ahead
RECOMMENDED_CHART_WINDOW = 2000      # Rows to display

PROMOTION_GATE_DEFAULTS = {
    "min_test_actionable": 0.525,
    "min_test_win_rate": 0.50,
    "min_test_alpha": 0.0005,
    "max_val_test_gap": 0.05,
    "max_test_cv": 0.50,
    "test_trade_rate_min": 0.40,
    "test_trade_rate_max": 0.80,
}
```

### Ticker Presets (market_data.py)

```python
TICKER_PRESETS = {
    "nvda": ("NVDA", "Nvidia", [...]),
    "aapl": ("AAPL", "Apple", [...]),
    "amd": ("AMD", "AMD", [...]),
    "mu": ("MU", "Micron", [...]),
    "amzn": ("AMZN", "Amazon", [...]),
    "googl": ("GOOGL", "Google", [...]),
}
```

---

## Risk Assessment & Critical Dependencies

### Risk Areas

- [ ] **Ensemble Config**: `staging/models/ensemble_config.json` is the single source of truth. Any corruption breaks dashboard.
- [ ] **Leaderboard CSVs**: Must exist and have required columns (model_path, test_trade_count, ranking_metric).
- [ ] **Model Files**: .zip files must exist at paths specified in leaderboard.
- [ ] **Data Path Compatibility**: Expected observation shape must match loaded data path.
- [ ] **Forward-Look Leakage**: Signal analytics must use strict split boundaries; test set must never see future data.

### Critical Files to Protect

| File | Why | Fallback |
|------|-----|----------|
| `staging/models/ensemble_config.json` | Defines production ensembles | Manual re-entry, but loses seed tracking |
| `data/experiment_leaderboard.csv` | Tracks all model results | Regenerate via `experiments.py` (slow) |
| `data/dashboard_signals/*.json` | Exported signals for dashboard | Re-run `export_signals_for_dashboard.py` |
| `.venv/` | Python dependencies | `pip install -r requirements.txt` |

### Breaking Changes to Watch

- Changing `LEADERBOARD_VERSION` in `trading_env.py` requires re-running all experiments
- Model format (.zip structure) changes require model re-export
- Signal schema changes require dashboard frontend updates
- Feature engineering changes require data recomputation

---

## Performance Considerations

### Model Loading
- Dashboard caches models in memory: `_load_model()` → pickle loading from .zip
- Multiple models can cause memory pressure; limit model_limit slider

### Data Loading
- Parquet format preferred over CSV (5–10x faster)
- Dashboard loads full dataset into memory; large data paths may cause slowdown

### Ensemble Inference
- Voting aggregation is fast; per-seed inference is O(n_seeds * n_bars)
- For production, consider caching signals for historical ranges

### GPU Acceleration
- Experiments can use CUDA (NVIDIA) or MPS (Apple Silicon)
- Dashboard typically runs on CPU (single inference per request)

---

## Documentation Map

| Document | Purpose | Audience |
|----------|---------|----------|
| `docs/TRADING_DASHBOARD_WIRING.md` | **Trading dashboard integration guide** | DevOps, Backend |
| `docs/TRADING_DASHBOARD_INTEGRATION.md` | Signal contract & schema | Frontend, Backend |
| `docs/EXECUTION_PROCESS.md` | How to run experiments end-to-end | Researchers |
| `docs/STAGE1_REGIME_SHIFT_REPORT.md` | Stage 1 results & regime analysis | Analysts |
| `docs/STAGE1_EXIT_REPORT.md` | Exit manager validation | Risk/Strategy |
| `docs/ENVIRONMENT_REALISM_AUDIT_2026_04_02.md` | Environment correctness audit | QA |
| `docs/AAPL_LEAKAGE_AUDIT.md` | Forward-look leakage detection | QA |
| `docs/GPU_ACCELERATION.md` | GPU setup & usage | DevOps |

---

## Quick Reference: File → Purpose

| File | Line # | Purpose |
|------|--------|---------|
| `src/dashboard/main.py` | 1–244 | Dashboard entry point & router |
| `src/ensemble.py` | 53–200+ | Multi-seed ensemble inference |
| `staging/models/ensemble_config.json` | 1–85 | Ensemble seed definitions |
| `src/signal_analytics.py` | - | Signal metrics (Sharpe, confusion, etc.) |
| `src/experiments.py` | 1–100+ | Walk-forward experiment orchestration |
| `src/trading_env.py` | 1–80+ | TradingEnv & PositionManager |
| `src/dashboard/pages/signal_analytics.py` | 35–100+ | Main analytics page |
| `src/dashboard/config.py` | 1–47 | Defaults & paths |
| `tests/test_ensemble.py` | - | Ensemble testing |
| `docs/TRADING_DASHBOARD_WIRING.md` | 1–189 | Dashboard integration guide |

---

**Last Updated:** 2026-07-04  
**Context Map Version:** 1.0  
**Status:** Complete & Current
