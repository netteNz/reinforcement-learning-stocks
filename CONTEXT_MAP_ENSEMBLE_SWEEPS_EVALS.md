# Context Map — Ensemble / Sweeps / Evals / Data / Docs

**Generated:** 2026-07-04
**Scope:** Inventory only — no code changes. Catalogs every file relevant to ensemble logic, sweep runs, evaluation scripts, data artifacts, and supporting docs across the repo.

Note: a broader, older `CONTEXT_MAP.md` (dated 2026-05-16, "Exit Signal Phase 3") already exists at repo root. This file is scoped narrower and more current — it doesn't replace that one.

---

## Ensemble

| File | Purpose |
|------|---------|
| `src/ensemble.py` (334 lines) | `SparseEnsemble` — loads Binary PPO seeds from leaderboard CSV, filters by `active_seeds`/`run_label`, majority-vote inference. Core ensemble logic. |
| `src/trading_agent.py` | `EnsembleAgent` — stateless live-inference wrapper around `SparseEnsemble`; reads `ensemble_config.json`. |
| `src/dashboard/components/ensemble.py` (66 lines) | Dashboard rendering component for ensemble voting/state. |
| `scripts/generate_ensemble_config.py` (127 lines) | Builds `ensemble_config.json` from leaderboard/promoted-seed data. |
| `staging/models/ensemble_config.json` | Staged ensemble config artifact (per-ticker seeds, weights). |
| `staging/src/ensemble.py` | Staged/frozen copy of ensemble module (compare against `src/ensemble.py` for drift before promoting staging → live). |
| `tests/test_ensemble.py` (5 lines) | Minimal/stub test coverage — thin, likely needs expansion. |
| `artifacts/ENSEMBLE_VOTING_DIAGNOSTIC_REPORT.md` | Diagnostic report on ensemble voting behavior/pathologies. |
| `artifacts/AMD_NVDA_MEAN_VOTING_FINDINGS.md` | Findings specific to mean-voting for AMD/NVDA ensembles. |
| `artifacts/QUANT_STRATEGY_ANALYSIS_MEAN_VOTING.md` | Quant analysis of mean-voting strategy performance. |
| `docs/archive/PATH_B_ENSEMBLE_PIPELINE_2026_04_29.md` | Archived design doc for the Path B ensemble pipeline. |

## Sweeps

| File | Purpose |
|------|---------|
| `EVAL_SWEEP.md` (root) | Primary doc describing the eval-sweep workflow. |
| `run_eval_sweep.sh` / `run_eval_sweep.ps1` (root) | Entry-point scripts to run an eval sweep (bash + PowerShell). |
| `scripts/evaluate_sweep.py` (438 lines) | Core sweep evaluation logic — likely aggregates per-config results into leaderboard rows. |
| `scripts/archive/legacy-runners/run_sweep.sh` / `.ps1` | Legacy sweep runners, superseded. |
| `scripts/archive/run_reward_calibration_sweep.ps1` | Archived reward-calibration sweep runner. |
| `scripts/archive/run_stage2_h1_sweep.ps1` / `run_stage2_h2_sweep.ps1` | Archived Stage 2 hypothesis sweep runners (H1/H2). |
| `data/audit/exit_signal_sweep/` | Sweep-specific exit-signal audit outputs (dir). |
| `data/experiment_snapshots/experiment_leaderboard_*_sweep-*.csv` and similarly named `*sweep*.csv` files | Dozens of dated leaderboard snapshots tagged by sweep name (e.g. `sweep-sharpe`, `sweep-sortino`, `amd-penalty-sweep-tp02/05/10`, `sweep_overtrade_fix_nvda*`, `sweep_amd_baseline_v1-4`, etc.) — historical sweep result CSVs. |
| `docs/archive/Analyzing MU Sweep Results.md` | Analysis doc for MU sweep results. |
| `sessions/SWEEP_ANALYSIS_2026-04-02.md` | Session log analyzing a sweep batch. |
| `sessions/session-2026-03-30-dashboard-and-sweeps.md` | Session log covering dashboard + sweep work. |

## Evals

| File | Purpose |
|------|---------|
| `scripts/evaluate_sweep.py` | (see above — sweep + eval overlap) |
| `scripts/evaluate_exit_backtest.py` (352 lines) | Evaluates exit-rule backtests (confidence/trailing_stop/time/profit_take/composite) against test data. |
| `scripts/archive/evaluate_stage1_trading.py` | Archived Stage 1 trading evaluation script. |
| `artifacts/stage1_recheck/stage1_trading_eval_recheck.json` | Rechecked Stage 1 trading eval output. |
| `artifacts/stage1_recheck/stage1_gate_report_recheck.json` / `.md` | Gate-pass recheck report (6-gate promotion criteria) tied to eval rerun. |
| `data/audit/exit_backtest/` | Per-ticker exit-backtest eval results: `amd_test_result.csv`, `amd_val_results.csv`, `mu_test_result.csv`, `mu_val_results.csv`, `nvda_test_result.csv`, `nvda_val_results.csv`, `backtest_summary.md`. |
| `data/audit/exit_signal_summary.csv` | Summary CSV of exit-signal eval results. |
| `data/audit/{amd,nvda}_exit_audit.csv` + `_summary.json` | Per-ticker exit audit eval detail + summary. |
| `results/stage1*/` (11 subdirs: `stage1`, `stage1_confirmation_3seed`, `stage1_rolling_window`, `stage1_step5`…`stage1_step11_nonlinear_fixed`) | Stage 1 baseline eval JSONs per ticker/model/horizon (e.g. `stage1_baseline_NVDA_xgb_1h.json`), one dir per experiment step/confirmation pass. |
| `results/stage2_h1` … `results/stage2_h4` | Stage 2 hypothesis-test eval outputs (H1–H4). |
| `reports/sanity_scan_report*.json`, `sanity_quarantine*.json`, `sanity_scan_summary.md` | Sanity/data-quality eval reports feeding into gate checks. |
| `src/rolling_window_validation.py` | Rolling-window validation logic used by eval/backtest scripts. |
| `src/signal_analytics.py` | Signal-level analytics consumed by eval/diagnostic reports. |

## Data files

| Location | Contents |
|------|---------|
| `data/experiment_leaderboard.csv`, `experiment_leaderboard_history.csv`, `experiment_reward_leaderboard*.csv` | Root leaderboard CSVs — current + full history, standard and reward-weighted variants. |
| `data/experiment_leaderboard_intraday_5m*.csv` | Intraday (5-minute) leaderboard variants (`_batch_a`, `_triggered`). |
| `data/experiment_summary*.json` | JSON rollups of experiment leaderboard state (per batch variant). |
| `data/experiment_snapshots/` (3999 entries) | Dated leaderboard CSV snapshots per experiment/sweep run — primary historical record of all sweeps. |
| `data/exp_1_nvda_10seed_foundation_*`, `exp_2_aapl_10seed_foundation_*`, `exp_3_amd_10seed_foundation_*` | 10-seed foundation experiment leaderboards + summaries + snapshot subdirs, per ticker. |
| `data/fork_b_option1_*`, `data/fork_b_option2_snapshots/` | "Fork B" experiment branch leaderboards/snapshots (Path B ensemble pipeline candidates). |
| `data/dashboard_signals/{amd,nvda}_signals.json` | Exported live/backtest signals feeding the trading dashboard. |
| `data/audit/` | Exit-signal and exit-backtest audit data (see Evals section) + `divergence_dashboard.png`, `phase_status_experiment_summary.png`, `phase_status_experiment_trace.png`. |
| `models/` | 6 serialized model artifacts (`.zip`/`.pkl` — SB3 PPO checkpoints, not enumerated individually). |
| `metadata/sanitization_log.json` | Log of data sanitization operations applied to leaderboard/experiment data. |
| `staging/metrics/{aapl,amd,nvda}_leaderboard.csv` | Staged leaderboard snapshots pending promotion. |
| `staging/models/ensemble_config.json` | Staged ensemble config (duplicate listing — see Ensemble section). |
| `backups/sanity_backup_2026-05-19T*/` | Point-in-time backups taken around sanitization runs. |

## Docs

| File | Purpose |
|------|---------|
| `PROJECT_STATE.md` (root) | Current overall project state — likely the most up-to-date single source of truth. |
| `HANDOFF.md` (root) + `docs/HANDOFF.md` + `docs/HANDOFF_PIVOTS.md` | Agent handoff docs (root one likely newest; `docs/` versions may be stale). |
| `EVAL_SWEEP.md` | Eval-sweep workflow doc (see Sweeps). |
| `EXIT_SIGNAL_TODO.md`, `OPTION_A_EXIT_SIGNAL_PLAN.md` | Exit-signal design/TODO docs. |
| `PPO_BINARY_STRATEGY.md` | Binary PPO strategy spec — referenced as needing an update in the older `CONTEXT_MAP.md`. |
| `RL_PANEL_IMPLEMENTATION.md`, `WIRING_TODO.md`, `DASHBOARD_GRAPH_TODO.md`, `MODULAR_DASHBOARD_REFACTOR_TODO.md`, `dashboard_modularization_todo.md` | Dashboard integration/refactor docs. |
| `REFINEMENT_TODO.md`, `QUICK_REFERENCE.md`, `SIGNAL_INTERPRETATION_AMD_NVDA.md`, `GOOGL_EXPS.md`, `session.md` | Misc working docs/notes. |
| `docs/` (root docs dir, 27 files) | `AAPL_LEAKAGE_AUDIT.md`, `ENVIRONMENT_REALISM_AUDIT_2026_04_02.md`, `IMPLEMENTATION_PLAN_ENVIRONMENT_REALISM.md`, `STAGE1_EXIT_REPORT.md`, `STAGE1_REGIME_SHIFT_REPORT.md`, `TIER2_EXECUTION_PLAN.md`, `TRADING_DASHBOARD_INTEGRATION.md`, `TRADING_DASHBOARD_WIRING.md`, `ROLLBACK_GUIDE.md`, `SANITIZE_APPLY_GUIDE.md` + `_QUICKSTART.md`, `stage2_h1_execution_checklist.md`, `stage2_h1_results_report_template.md`, `stage2_next_steps_checklist.md`, `INDEX.md`, `PLAN.md`, `PROJECT_COMPLETION.md`, `COMPLETION_CHECKLIST.md`, `DELIVERABLES.md`, `GPU_ACCELERATION.md`, `SENTIMENT_INTEGRATION.md`, `GEMINI_HANDOFF_REWARD_HYBRID_FIX.md`, `PHASE_1_COMPLETE.md`, `implementation_plan.md`. |
| `docs/archive/` (18 files) | Older/superseded docs: `PATH_B_ENSEMBLE_PIPELINE_2026_04_29.md`, `Analyzing MU Sweep Results.md`, `CLAUDE_HANDOFFV2.md`, `PROJECT_STATE_2026_04_29.md` (+ `UPDATED_`), `PROJECT_PIVOT_ASSESSMENT_2026_04_29.md`, `DECISION_PATH_A_vs_B.md`, `EXPERIMENT_EXECUTION_README.md`, `EXPERIMENT_SUITE_PATH_B_v1.md`, `gemini_doc.md`, `README_HANDOFF.md`, `stage2_experiment_brief.md`, `stage2_gate_definitions.md`, `stages.md`, `assessment.md`. |
| `CONTEXT_MAP.md` (root, existing) | Prior context map dated 2026-05-16 (Exit Signal Phase 3 focus) — now partially stale given commits since (exit strategy updates, new dashboard docs). |
| `staging/STAGING_READY.md` | Readiness checklist for promoting staged models/config to production. |

---

## Adjacent / Out-of-Scope

- **`event-research/`** — separate research pipeline (config/schemas/scripts for news/event panels). Not part of the ensemble/sweep/eval trading loop; flagged only for completeness, not detailed above.
- **`quarantine/`, `archives/`, `scratch/`** — exist at root; not inspected in depth (housekeeping/quarantined data, not active ensemble/sweep/eval surfaces).

## Risk / Staleness Flags

- [ ] `tests/test_ensemble.py` is only 5 lines — effectively no real test coverage for `SparseEnsemble`.
- [ ] `staging/src/ensemble.py` may have drifted from `src/ensemble.py` (13,965 bytes vs staged copy) — diff before next promotion.
- [ ] Root `CONTEXT_MAP.md` and several `docs/` handoff files predate the most recent commits (exit strategy + dashboard updates) — treat as historical, verify against `PROJECT_STATE.md`/git log before relying on them.
- [ ] `data/experiment_snapshots/` has ~3999 files — useful as history but expensive to scan; prefer `data/experiment_leaderboard*.csv` for current state.
