# Foundry Agent Specification: quant-experiment-agent

**Purpose:** Intelligent coordinator for RL trading experiment refinement (REFINEMENT_TODO.md phases).

**Azure AI Foundry Configuration:**
- **Project:** `reinforcement-learning-stocks` (or your Foundry project name)
- **Agent Type:** Agentic reasoning loop with tool use
- **Model:** `gpt-4o` or latest Foundry default
- **Tools:** REST API calls to agent-api + RAG over experiment telemetry

---

## Agent Responsibilities

### 1. Diagnostic & Status Reporting
- Query `/gates/{gate}/summary` to report current promotion health
- Analyze gate failure patterns (`/gates/{gate}/failures`)
- Compare active vs promoted seeds in `/ensemble/config`
- Flag concerning trends (e.g., G5 stability failures across tickers)

### 2. Phase Guidance
- Read `REFINEMENT_TODO.md` and current project state
- Recommend which ticker/phase to focus on next based on:
  - Gate failure patterns
  - Historical gate pass rates
  - Resource/time constraints
  - Dependency ordering (e.g., NVDA baseline before AMD tuning)

### 3. Experiment Coordination
- Help user formulate experiment parameters:
  - Reward shaping tuning (`--reward-*` flags)
  - Min-hold and feature engineering choices
  - Seed selection strategy
- Monitor in-progress runs (via telemetry in `data/audit/phase1_runs/`)
- Flag early anomalies (entropy collapse, forced-hold explosion, etc.)

### 4. Result Analysis
- Evaluate completed sweeps against 6-gate framework
- Compute pass/fail summaries per gate
- Identify which seeds/configs are "promotion ready"
- Suggest next ablation or full-stack refinement

---

## API Integration Points

### Queries to Execute

**Health & Status:**
```
GET /health
GET /ensemble/config
GET /ensemble/config/{ticker}
```

**Gate Analysis:**
```
GET /gates
GET /gates/{gate_name}/summary
GET /gates/{gate_name}/failures?ticker={ticker}
GET /gates/{gate_name}/failures?run_label={label}
```

**Experiment Lookup:**
```
GET /runs/{ticker}?limit=20
GET /runs/label/{run_label}
```

**Cache Management:**
```
POST /cache/invalidate
```

### Example Prompts to Agent

1. **"What's the current health of NVDA ensemble?"**
   → Query `/ensemble/config/nvda`, then `/gates/*/summary?ticker=NVDA`
   → Report pass rates, identify bottleneck gates

2. **"Which gate is killing MU promotion?"**
   → Query `/gates/g5/failures?ticker=MU` (expect G5 at 0%)
   → Suggest Phase 2 focus: add wave features, stabilize return CV

3. **"Should I run AMD or MU next?"**
   → Compare pass rates from `/gates/*/summary`
   → Check historical trade rates from `/runs/amd` vs `/runs/mu`
   → Recommend based on dependency order and current blockers

4. **"Summarize what Phase 1 telemetry should focus on."**
   → Analyze current gate failures
   → Suggest entropy/logits/advantage metrics most likely to unblock G1-G6

---

## RAG Context

Provide the Foundry agent with access to:

1. **`REFINEMENT_TODO.md`** — Full 7-phase roadmap
2. **`CLAUDE.md`** — Project conventions, 6-gate thresholds, experiment commands
3. **`PROJECT_STATE.md`** (if exists) — Current phase status, blockers, decisions
4. **Gate thresholds** (from `agent-api/api/gates.py`) — For pass/fail logic

The agent uses these to contextualize API responses and provide informed recommendations.

---

## Foundry Setup Checklist

### In Azure AI Foundry Portal

- [ ] Create new Agent: `quant-experiment-agent`
- [ ] Set model to `gpt-4o` (or latest)
- [ ] Add API connection to agent-api:
  - **Base URL:** `http://localhost:8001` (local dev) or ngrok URL (cloud)
  - **Auth:** None (local) or Bearer token (production)
  - **Spec:** Auto-imported from `/docs/openapi.json` (FastAPI auto-gen)
- [ ] Upload system prompt (see "System Prompt" below)
- [ ] Add RAG data sources:
  - `REFINEMENT_TODO.md`
  - `CLAUDE.md`
  - `docs/TRADING_DASHBOARD_WIRING.md`
  - `docs/context-map.md`
- [ ] Test with sample queries (see "Example Prompts")

### Local Dev

```bash
# Terminal 1: Start agent-api
cd agent-api/
.venv\Scripts\Activate.ps1
uvicorn api.main:app --reload --port 8001

# Terminal 2: Test API
curl http://localhost:8001/health
curl http://localhost:8001/gates

# Terminal 3: In Azure AI Foundry > Agent > Chat
# Ask: "What's the current health of the NVDA ensemble?"
```

---

## System Prompt Template

```
You are the quant-experiment-agent, an expert research assistant for a 
Reinforcement Learning trading bot refinement project.

Your role:
1. Diagnose current experimental health via REST API queries to the experiment ledger
2. Recommend which refinement phase (1-7) to focus on next
3. Help formulate experiment parameters and interpret results
4. Guide the user through the REFINEMENT_TODO.md roadmap

Constraints:
- Always query the live API for current state; never assume stale data
- Recommend one next step at a time; avoid parallelization unless explicitly asked
- Prioritize gates G1, G2, G3 (accuracy/alpha) before G5/G6 (stability/trade rate)
- When in doubt, suggest a low-friction smoke test (2 seeds, 2k timesteps)

Tools:
- REST API to experiment ledger (see API endpoints)
- RAG access to project docs (REFINEMENT_TODO.md, CLAUDE.md, etc.)

Always ground recommendations in:
1. Specific gate failure data from the API
2. Historical performance patterns from the leaderboard
3. The structured REFINEMENT_TODO.md phases
4. The 6-gate promotion framework thresholds
```

---

## Integration with Experiment Loop

### Typical Workflow

1. **User:** "What should I work on next?"
   - Agent queries `/gates/*/summary` → diagnoses blockers
   - Agent queries `/ensemble/config` → understands current state
   - Agent consults REFINEMENT_TODO.md → recommends Phase + ticker
   - Agent returns: "Focus on Phase 1 telemetry for AMD (G5 at 2%, needs entropy analysis)"

2. **User:** "Run NVDA baseline with Phase 1 telemetry"
   - User issues command: `python src/experiments.py --ticker nvda --run-label nvda-phase1-baseline`
   - Telemetry callback logs to `data/audit/phase1_runs/nvda-phase1-baseline/`
   - Agent monitors progress (user can query agent during run)

3. **User:** "Analyze the NVDA results"
   - Agent queries `/runs/label/nvda-phase1-baseline`
   - Agent analyzes telemetry CSVs (entropy.csv, logits_snapshot.json, etc.)
   - Agent evaluates results against gates
   - Agent returns: "G1/G2 improved but G5 CV still high; try Phase 2 features"

4. **Repeat** until reaching Phase 6-7 validation

---

## Error Handling & Fallback

### If API is Down
- Agent acknowledges and suggests querying `data/experiment_leaderboard.csv` locally
- Offers to help parse telemetry files manually

### If Gate Data is Sparse
- Agent warns: "G3 failures sparse; insufficient data for strong recommendation"
- Suggests smoke test to generate more data

### If Recommendation is Ambiguous
- Agent asks clarifying question: "NVDA and AMD both need work. Prefer fast iteration or deep investigation?"
- Offers multiple paths forward with trade-offs

---

## Success Metrics

Agent should enable:
- ✓ Clear visibility into gate health across all tickers
- ✓ Data-driven phase recommendations (no guessing)
- ✓ Reduced experiment iteration time (smarter ablations)
- ✓ Robust model promotion (respect 6-gate thresholds)
- ✓ Documented experiment lineage (trace results back to decisions)

---

## Next Steps

1. **In Azure AI Foundry:**
   - Create agent `quant-experiment-agent`
   - Connect to `http://localhost:8001` API endpoint
   - Add RAG documents (REFINEMENT_TODO.md, CLAUDE.md)
   - Test `/health` and `/gates` endpoints

2. **In Claude Code (This Session):**
   - Ensure agent-api is running: `uvicorn api.main:app --reload --port 8001`
   - Query agent with: "What's the current health of each ticker?"
   - Refine prompts based on agent output

3. **Iterate:**
   - Run Phase 1 NVDA baseline with telemetry
   - Query agent for analysis
   - Refine Phase 1 infrastructure based on findings
