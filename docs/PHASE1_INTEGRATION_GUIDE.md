# Phase 1 Telemetry Integration — Quick Reference

**Goal:** Wire Phase1TelemetryCallback into experiments.py so training logs telemetry.

---

## Integration Checklist

### 1. Verify src/phase1_telemetry.py exists
```bash
ls -la src/phase1_telemetry.py  # Should exist
```

### 2. Locate the model.learn() call in src/experiments.py
Find the line where the policy is trained. It will look like:
```python
model.learn(
    total_timesteps=timesteps,
    ...
)
```

### 3. Add the telemetry callback
**Before** the `model.learn()` call, add:
```python
from src.phase1_telemetry import Phase1TelemetryCallback

# Construct callback
telemetry_log_dir = f"data/audit/phase1_runs/{run_label}"
callback = Phase1TelemetryCallback(
    log_dir=telemetry_log_dir,
    ticker=ticker,
    seed=seed,
    sample_frequency=10  # Log every 10th step
)

# Pass to learn()
model.learn(
    total_timesteps=timesteps,
    callback=callback,  # ADD THIS LINE
    ...
)

# Finalize after training completes
callback.finalize_run()
```

### 4. Test with smoke run
```bash
# Terminal
cd D:\code\agentic-development\reinforcement-learning-stocks
.venv\Scripts\Activate.ps1

# Smoke test (1 seed, 1k timesteps)
python src/experiments.py \
  --ticker nvda \
  --seeds 3 \
  --binary-actions \
  --timesteps 1000 \
  --run-label nvda-smoke-phase1 \
  --max-runs 1

# Verify telemetry was written
ls -la data/audit/phase1_runs/nvda-smoke-phase1/
# Expected files:
#   entropy.csv
#   advantages.csv
#   critic_values.csv
#   forced_holds.csv
#   logits_snapshot.json
#   summary.json
```

### 5. Inspect telemetry output
```bash
# Check entropy distribution
head -20 data/audit/phase1_runs/nvda-smoke-phase1/entropy.csv

# Check summary metrics
cat data/audit/phase1_runs/nvda-smoke-phase1/summary.json | python -m json.tool
```

**Expected output in summary.json:**
```json
{
  "ticker": "nvda",
  "seed": 3,
  "entropy": {
    "mean": 0.65,
    "std": 0.12,
    "min": 0.01,
    "max": 1.38
  },
  "action_distribution": {
    "buy": 0.62,
    "hold": 0.38
  },
  "forced_holds_count": 145
}
```

---

## What to Look For

### Healthy Telemetry
- **Entropy**: Mean 0.5-0.8 (policy is stochastic, not collapsed)
- **Action Distribution**: Buy 40-60%, Hold 40-60% (not skewed)
- **Forced Holds**: < 20% of total steps (min_hold constraint not choking policy)

### Red Flags
- **Entropy**: Mean < 0.2 (policy collapsed to deterministic)
- **Action Distribution**: Buy > 85% (strong buy bias)
- **Forced Holds**: > 50% of steps (constraint overwhelming training signal)

---

## Integration Points

The callback needs to be wired in **two places**:

1. **Training Loop** (src/experiments.py)
   - During `model.learn()` call
   - Logs per-step data in real-time

2. **Post-Training** (in experiments.py)
   - Call `callback.finalize_run()` after training completes
   - Writes summary.json, logits_snapshot.json

### Minimal Code Change Example

```python
# In src/experiments.py, around the training loop:

from src.phase1_telemetry import Phase1TelemetryCallback  # ADD THIS IMPORT

# ... earlier code ...

for seed in seeds:
    # ... setup env, model, etc ...

    # Create callback
    callback = Phase1TelemetryCallback(  # ADD THIS BLOCK
        log_dir=f"data/audit/phase1_runs/{run_label}",
        ticker=ticker,
        seed=seed,
    )

    # Train with callback
    model.learn(
        total_timesteps=timesteps,
        callback=callback,  # ADD THIS LINE
        # ... other args ...
    )

    # Finalize telemetry
    callback.finalize_run()  # ADD THIS LINE

    # ... rest of training logic ...
```

---

## Checking Integration Success

After running a smoke test, verify:

1. **Telemetry files exist:**
   ```bash
   test -f data/audit/phase1_runs/nvda-smoke-phase1/entropy.csv && echo "OK" || echo "MISSING"
   ```

2. **Entropy.csv has data:**
   ```bash
   wc -l data/audit/phase1_runs/nvda-smoke-phase1/entropy.csv  # Should be > 100
   ```

3. **Summary.json is valid:**
   ```bash
   python -c "import json; json.load(open('data/audit/phase1_runs/nvda-smoke-phase1/summary.json'))" && echo "OK"
   ```

4. **Action distribution computed:**
   ```bash
   python -c "import json; s=json.load(open('data/audit/phase1_runs/nvda-smoke-phase1/summary.json')); print(s['action_distribution'])"
   # Expected: {'buy': 0.6X, 'hold': 0.3X}
   ```

---

## Troubleshooting

**Problem:** `ModuleNotFoundError: No module named 'src.phase1_telemetry'`
- **Fix:** Ensure you're running from repo root: `cd D:\code\agentic-development\reinforcement-learning-stocks`

**Problem:** Telemetry files not created
- **Fix:** Check callback instantiation — ensure `log_dir` exists (callback creates it)
- **Fix:** Verify `callback.finalize_run()` is called after `model.learn()`

**Problem:** Entropy.csv is empty
- **Fix:** Check if callback.log_step() is being called — may need to verify callback integration in training loop

---

## Next: Query Agent for Analysis

Once telemetry is flowing, query the Foundry agent:

```
User: "I ran NVDA with Phase 1 telemetry. The entropy is mean=0.35, 
buy_ratio=0.85. What's this telling us?"

Agent (using telemetry):
1. Interprets entropy collapse (0.35 < 0.5 threshold)
2. Notes heavy buy bias (85% > 60%)
3. Queries /gates/g1/failures?ticker=NVDA
4. Returns: "Entropy collapse explains G1 accuracy failures. 
   The policy became deterministic. Reduce ent_coef penalty or 
   increase action_bonus_scale to restore stochasticity."
```

---

## References

- **src/phase1_telemetry.py** — Telemetry implementation
- **PHASE1_INFRASTRUCTURE.md** — Full roadmap + status
- **FOUNDRY_AGENT_SPEC.md** — Agent design + API endpoints
