"""
Phase 1 Telemetry Callback: Actor logits, entropy, critic value, advantages.

SB3 BaseCallback subclass — hooks into model.learn() via _on_step() and pulls
live policy internals (pre-mask logits, entropy, value estimate) plus
env-level constraint state (cooldown / forced holds).

Usage (see src/experiments.py around the model.learn() call):

    from src.phase1_telemetry import Phase1TelemetryCallback

    telemetry_cb = Phase1TelemetryCallback(
        log_dir=f"data/audit/phase1_runs/{run_label}",
        ticker=ticker,
        seed=seed,
    )
    model.learn(total_timesteps=timesteps, callback=[callback, telemetry_cb])
    telemetry_cb.finalize_run()

Output structure:
  data/audit/phase1_runs/{run_label}/seed{seed}/
    ├── entropy.csv          (per-step entropy, action, logits, position)
    ├── advantages.csv       (value estimate, cooldown/forced-hold flags)
    ├── logits_snapshot.json (sampled raw actor logits)
    └── summary.json         (aggregated metrics)
"""

import csv
import json
from pathlib import Path

import numpy as np
import torch
from stable_baselines3.common.callbacks import BaseCallback


class Phase1TelemetryCallback(BaseCallback):
    """Captures actor logits, policy entropy, critic value, and forced-hold
    constraint hits during PPO/MaskablePPO training."""

    def __init__(
        self,
        log_dir: str,
        ticker: str,
        seed: int = 0,
        sample_frequency: int = 10,
        max_snapshots: int = 200,
        verbose: int = 0,
    ):
        super().__init__(verbose)
        self.log_dir = Path(log_dir) / f"seed{seed}"
        self.log_dir.mkdir(parents=True, exist_ok=True)

        self.ticker = ticker
        self.seed = seed
        self.sample_frequency = sample_frequency
        self.max_snapshots = max_snapshots

        self.entropy_file = self.log_dir / "entropy.csv"
        self.advantages_file = self.log_dir / "advantages.csv"
        self.logits_snapshots: list[dict] = []

        self._init_csv_files()

    def _init_csv_files(self):
        with open(self.entropy_file, "w", newline="") as f:
            csv.writer(f).writerow([
                "step", "action", "entropy", "logit_0", "logit_1", "action_prob", "position"
            ])
        with open(self.advantages_file, "w", newline="") as f:
            csv.writer(f).writerow([
                "step", "value_estimate", "in_cooldown", "forced_action"
            ])

    def _on_step(self) -> bool:
        if self.n_calls % self.sample_frequency != 0:
            return True

        obs_tensor = self.locals.get("obs_tensor")
        if obs_tensor is None:
            new_obs = self.locals.get("new_obs")
            if new_obs is None:
                return True
            obs_tensor, _ = self.model.policy.obs_to_tensor(new_obs)

        with torch.no_grad():
            features = self.model.policy.extract_features(obs_tensor)
            latent_pi, latent_vf = self.model.policy.mlp_extractor(features)
            distribution = self.model.policy._get_action_dist_from_latent(latent_pi)
            logits = distribution.distribution.logits.cpu().numpy()[0]
            probs = torch.softmax(distribution.distribution.logits, dim=-1).cpu().numpy()[0]
            entropy = float(distribution.entropy().cpu().numpy()[0])
            value = float(self.model.policy.value_net(latent_vf).cpu().numpy().flatten()[0])

        actions = self.locals.get("actions")
        action = int(actions[0]) if actions is not None else -1

        # Pull constraint state from the underlying env if it exposes it
        envs = getattr(self.training_env, "envs", None)
        position = None
        in_cooldown = False
        forced_action = False
        if envs:
            base_env = envs[0]
            pm = getattr(base_env, "pm", None) or getattr(base_env.unwrapped, "pm", None)
            if pm is not None:
                position = float(getattr(pm, "current_weight", np.nan))
            action_masks_fn = getattr(base_env, "action_masks", None) or getattr(base_env.unwrapped, "action_masks", None)
            if action_masks_fn is not None:
                mask = action_masks_fn()
                in_cooldown = bool(mask is not None and not all(mask))
                if in_cooldown and mask is not None:
                    forced_action = not bool(mask[action]) if 0 <= action < len(mask) else False

        with open(self.entropy_file, "a", newline="") as f:
            csv.writer(f).writerow([
                self.num_timesteps, action, entropy,
                float(logits[0]), float(logits[1]) if len(logits) > 1 else None,
                float(probs[action]) if 0 <= action < len(probs) else None,
                position,
            ])

        with open(self.advantages_file, "a", newline="") as f:
            csv.writer(f).writerow([self.num_timesteps, value, in_cooldown, forced_action])

        if len(self.logits_snapshots) < self.max_snapshots:
            self.logits_snapshots.append({
                "step": self.num_timesteps,
                "logits": logits.tolist(),
                "action": action,
                "entropy": entropy,
            })

        return True

    def finalize_run(self):
        logits_path = self.log_dir / "logits_snapshot.json"
        with open(logits_path, "w") as f:
            json.dump({
                "ticker": self.ticker,
                "seed": self.seed,
                "snapshots": self.logits_snapshots,
            }, f, indent=2)

        summary = self._compute_summary()
        (self.log_dir / "summary.json").write_text(json.dumps(summary, indent=2))

    def _compute_summary(self) -> dict:
        import pandas as pd

        summary = {"ticker": self.ticker, "seed": self.seed}

        if self.entropy_file.exists():
            df = pd.read_csv(self.entropy_file)
            if len(df):
                summary["entropy"] = {
                    "mean": float(df["entropy"].mean()),
                    "std": float(df["entropy"].std()),
                    "min": float(df["entropy"].min()),
                    "max": float(df["entropy"].max()),
                }
                summary["action_distribution"] = {
                    "action_0_flat": float((df["action"] == 0).mean()),
                    "action_1_long": float((df["action"] == 1).mean()),
                }
                summary["mean_action_prob"] = float(df["action_prob"].mean())

        if self.advantages_file.exists():
            df = pd.read_csv(self.advantages_file)
            if len(df):
                summary["value_estimate_mean"] = float(df["value_estimate"].mean())
                summary["in_cooldown_ratio"] = float(df["in_cooldown"].mean())
                summary["forced_action_ratio"] = float(df["forced_action"].mean())

        return summary
