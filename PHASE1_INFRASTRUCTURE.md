# Phase 1 Infrastructure — Ready for Foundry Coordination

**Status:** Infrastructure laid out. Ready to run diagnostics and first telemetry sweep.

---

## What We've Built

### 1. Diagnostic Script (`scripts/phase1_diagnostic.py`)
**Purpose:** Snapshot current health of promoted models.

**Output:**
```
PROMOTED TICKERS:
  NVDA  | Seeds: [3, 13, 7, 42] | Sharpe: 1.86 | min_hold: 1
  AMD   | Seeds: [21]           | Sharpe: 1.159 | min_hold: 3
  MU    | Seeds: [3, 7, 42]     | (monitor mode)

CRITICAL FINDINGS:
  NVDA  G1: 5%   | G2: 5%   | G3: 4%   | G4: 50% | G5: 3% | G6: 4%
  AMD   G1: 11%  | G2: 11%  | G3: 10%  | G4: 92% | G5: 2% | G6: 10%
  MU    G1: 15%  | G2: 15%  | G3: 12%  | G4: 82% | G5: 0% | G6: 15%
```

**Interpretation:**
- **G1-G3 Blockers:** Actionable accuracy (<53%), win rate (<50%), alpha (<0.05%) are all failing hard
- **G5 Emergency (MU):** Zero models pass return CV gate; extreme instability
- **G4 Passes:** Val/test drift is relatively OK (NVDA 50%, AMD 92%, MU 82%)
- **G6 Fails:** Trade rates out of [0.40, 1.00] range

**Action:** The "promoted" ensemble needs immediate refinement. Phase 1 telemetry will diagnose why.

---

### 2. Telemetry Capture (`src/phase1_telemetry.py`)
**Purpose:** Instrument PPO policy to capture actor logits, entropy, critic value, advantages during training.

**What It Logs:**
- `entropy.csv` — Policy entropy H(π) per timestep, action distribution
- `logits_snapshot.json` — Raw actor logits (before masking)
- `advantages.csv` — Advantage estimates, cooldown constraint violations
- `critic_values.csv` — V(s) predictions vs realized returns
- `forced_holds.csv` — min_hold_bars constraint fires
- `summary.json` — Aggregated metrics (mean entropy, action ratios, etc.)

**Output Structure:**
```
data/audit/phase1_runs/{run_label}/
  ├── entropy.csv
  ├── logits_snapshot.json
  ├── advantages.csv
  ├── critic_values.csv
  ├── forced_holds.csv
  └── summary.json
```

**Integration:** Pass callback to `model.learn()`:
```python
from src.phase1_telemetry import Phase1TelemetryCallback

callback = Phase1TelemetryCallback(
    log_dir="data/audit/phase1_runs/nvda-baseline-v1",
    ticker="nvda",
    seed=3
)
# model.learn(..., callback=callback)
```

---

### 3. Foundry Agent Specification (`docs/FOUNDRY_AGENT_SPEC.md`)
**Purpose:** Design for intelligent experiment coordinator using Azure AI Foundry.

**Agent Capabilities:**
1. **Diagnostic Queries** → `/health`, `/gates/*/summary`, `/ensemble/config`
2. **Gate Analysis** → Identify which gates are blocking promotion
3. **Phase Recommendations** → Based on current blockers + REFINEMENT_TODO.md
4. **Result Interpretation** → Evaluate completed runs against 6-gate thresholds
5. **Parameter Assistance** → Help formulate reward-tuning, feature engineering choices

**Integration Points:**
- **API Endpoint:** `http://localhost:8001` (agent-api)
- **RAG Sources:** REFINEMENT_TODO.md, CLAUDE.md, context-map.md
- **System Prompt:** Provided in spec

---

## Phase 1 Execution Plan

### Step 1: Start Agent-API (Local Dev)
```bash
# Terminal 1
cd agent-api/
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
uvicorn api.main:app --reload --port 8001

# Verify
curl http://localhost:8001/health
```

### Step 2: Create Foundry Agent (Azure Portal)
1. Go to **Azure AI Foundry** → Your project
2. Create new **Agent**: `quant-experiment-agent`
3. Set model: `gpt-4o` (or latest)
4. Add tool: REST API to `http://localhost:8001`
5. Upload RAG documents:
   - `REFINEMENT_TODO.md`
   - `CLAUDE.md`
   - `docs/FOUNDRY_AGENT_SPEC.md`
6. Use system prompt from `FOUNDRY_AGENT_SPEC.md`
7. Test with query: **"What's the current health of each ticker?"**

### Step 3: Run NVDA Phase 1 Baseline
```bash
# Command to execute (user will run this)
python src/experiments.py \
  --ticker nvda \
  --seeds 3,13 \
  --binary-actions \
  --timesteps 10000 \
  --run-label nvda-phase1-baseline \
  --max-runs 2

# Expected output:
# - Models trained in staging/models/nvda/
# - Leaderboard updated: data/experiment_leaderboard_history.csv
# - Phase 1 telemetry: data/audit/phase1_runs/nvda-phase1-baseline/
```

**With Telemetry Integration:**
The callback must be wired into `src/experiments.py` before running (see Step 4 below).

### Step 4: Wire Telemetry into experiments.py
**Required Change:** In `src/experiments.py`, add Phase1TelemetryCallback to the training loop.

**Location:** Near `model.learn()` call, add:
```python
from src.phase1_telemetry import Phase1TelemetryCallback

# Inside experiment loop
callback = Phase1TelemetryCallback(
    log_dir=f"data/audit/phase1_runs/{run_label}",
    ticker=ticker,
    seed=seed
)
model.learn(total_timesteps=timesteps, callback=callback)
callback.finalize_run()
```

### Step 5: Query Agent for Analysis
```
User: "Analyze the NVDA baseline results. What's the entropy telling us?"

Agent:
1. Queries `/runs/label/nvda-phase1-baseline`
2. Reads data/audit/phase1_runs/nvda-phase1-baseline/entropy.csv
3. Compares entropy trends to gate failures
4. Returns: "Entropy collapsed at bar 500; policy became deterministic.
   This explains G1 accuracy failure. Recommend: reduce ent_coef penalty."
```

---

## Current Infrastructure Status

| Component | Status | Path |
|-----------|--------|------|
| Diagnostic script | ✓ Ready | `scripts/phase1_diagnostic.py` |
| Telemetry module | ✓ Ready | `src/phase1_telemetry.py` |
| Foundry agent spec | ✓ Ready | `docs/FOUNDRY_AGENT_SPEC.md` |
| Agent-API | ✓ Running | `agent-api/api/main.py` |
| Audit directories | ✓ Ready | `data/audit/phase1_runs/`, etc. |

| Integration | Status | Notes |
|-----------|--------|-------|
| experiments.py telemetry wiring | ⚠ Pending | Need to add Phase1TelemetryCallback to training loop |
| Foundry agent creation | ⚠ Pending | Create in Azure portal; point to localhost:8001 |
| End-to-end test | ⚠ Pending | Run NVDA baseline, query agent |

---

## Next Immediate Actions

### For Claude:
1. **Wire telemetry into experiments.py**
   - Add Phase1TelemetryCallback to training loop
   - Test with smoke run (2 seeds, 1k timesteps)

2. **Verify agent-api endpoints**
   - Ensure FastAPI is serving at /docs
   - Test: `curl http://localhost:8001/gates/g1/summary`

### For User (in Azure AI Foundry):
1. Create agent `quant-experiment-agent`
2. Connect to `http://localhost:8001`
3. Add RAG sources (REFINEMENT_TODO.md, etc.)
4. Test with: "What's blocking AMD promotion?"

### Then:
1. Run NVDA Phase 1 baseline with telemetry
2. Query Foundry agent: "Analyze entropy and gate failures"
3. Iterate on Phase 1 findings
4. Proceed to Phase 2 (wave-aware features)

---

## Success Criteria for Phase 1

- [ ] Agent-API running, all endpoints responding
- [ ] Foundry agent created, can query `/gates/*/summary`
- [ ] NVDA baseline run completes with telemetry
- [ ] Agent can interpret entropy/logits findings
- [ ] Clear diagnosis of why G1-G6 pass rates are low
- [ ] Actionable recommendation for Phase 2 (e.g., "add wave features" or "reduce hold penalty")

---

## References

- **REFINEMENT_TODO.md** — 7-phase roadmap
- **FOUNDRY_AGENT_SPEC.md** — Agent design + setup checklist
- **CLAUDE.md** — Project conventions + 6-gate thresholds
- **agent-api/README.md** — API setup & endpoints
- **phase1_diagnostic.py** — Current health snapshot
- **phase1_telemetry.py** — Telemetry capture implementation
