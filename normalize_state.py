#!/usr/bin/env python3
"""
normalize_state.py — canonical JSON snapshot of repo state, plus a built-in
comparator so you don't hand-diff two files every time.

USAGE
  Scan mode (run on each machine, from repo root):
      python normalize_state.py

  Compare mode (run anywhere, once you have both machines' output):
      python normalize_state.py --compare state_snapshot_A.json state_snapshot_B.json

Pure stdlib. No OS-specific paths — same file runs unmodified on Windows/Mac/Pi.
"""
import json
import csv
import sys
import argparse
from pathlib import Path
from datetime import datetime, timezone
import socket

REPO_ROOT = Path(__file__).resolve().parent
STAGING = REPO_ROOT / "staging"
PROD_MODELS = REPO_ROOT / "models"
SNAPSHOTS = REPO_ROOT / "data" / "experiment_snapshots"

MODEL_EXTS = {".zip", ".pkl"}


def machine_tag():
    return socket.gethostname()


def scan_staged_models():
    """staging/models/<ticker>/<ticker>_seed<N>.zip -> {ticker: [seeds]}"""
    result = {}
    models_dir = STAGING / "models"
    if not models_dir.exists():
        return result
    for ticker_dir in sorted(p for p in models_dir.iterdir() if p.is_dir()):
        seeds = []
        for f in sorted(ticker_dir.glob(f"{ticker_dir.name}_seed*.zip")):
            seed_num = f.stem.split("seed")[-1]
            seeds.append({
                "seed": seed_num,
                "file": f.name,
                "size_bytes": f.stat().st_size,
            })
        result[ticker_dir.name.upper()] = seeds
    return result


def scan_production_models():
    """
    Top-level models/ — the promoted/production checkpoints, distinct from
    staging/models/. This is what the original hand-written context maps
    referenced ("6 serialized model artifacts") but earlier script versions
    never actually scanned.
    """
    if not PROD_MODELS.exists():
        return {"exists": False, "files": []}
    files = []
    for f in sorted(PROD_MODELS.iterdir()):
        if f.is_file() and f.suffix.lower() in MODEL_EXTS:
            files.append({
                "file": f.name,
                "ext": f.suffix.lower(),
                "size_bytes": f.stat().st_size,
                "modified": datetime.fromtimestamp(
                    f.stat().st_mtime, tz=timezone.utc
                ).isoformat(),
            })
    return {"exists": True, "count": len(files), "files": files}


def scan_staging_src():
    src_dir = STAGING / "src"
    if not src_dir.exists():
        return []
    return sorted(f.name for f in src_dir.glob("*.py"))


def read_ensemble_config():
    cfg_path = STAGING / "models" / "ensemble_config.json"
    if not cfg_path.exists():
        return None
    try:
        return json.loads(cfg_path.read_text())
    except json.JSONDecodeError:
        return {"_error": "unparseable JSON", "_path": str(cfg_path)}


def scan_snapshot_leaderboards():
    if not SNAPSHOTS.exists():
        return {"exists": False, "count": 0, "files": []}
    files = list(SNAPSHOTS.glob("*.csv"))
    summary = []
    for f in sorted(files):
        try:
            with f.open(newline="", encoding="utf-8", errors="replace") as fh:
                row_count = sum(1 for _ in csv.reader(fh)) - 1
        except Exception:
            row_count = None
        summary.append({
            "file": f.name,
            "rows": row_count,
            "size_bytes": f.stat().st_size,
        })
    return {"exists": True, "count": len(files), "files": summary}


def scan_fork_b():
    result = {}
    for opt in ("fork_b_option1_snapshots", "fork_b_option2_snapshots"):
        d = REPO_ROOT / "data" / opt
        result[opt] = sorted(f.name for f in d.glob("*")) if d.exists() else None
    return result


def find_active_seed_mismatches(ensemble_config, staged_models):
    """
    Flag any ticker where ensemble_config's active_seeds don't match what's
    physically staged. Confirmed present on both Mac/Windows for AMD/NVDA —
    this check makes it automatic instead of eyeballed.
    """
    mismatches = []
    if not ensemble_config:
        return mismatches
    for ticker_lower, cfg in ensemble_config.items():
        ticker = ticker_lower.upper()
        active = set(str(s) for s in cfg.get("active_seeds", []))
        staged = set(s["seed"] for s in staged_models.get(ticker, []))
        if not active and not staged:
            continue
        if active != staged:
            mismatches.append({
                "ticker": ticker,
                "config_active_seeds": sorted(active, key=lambda x: int(x)),
                "staged_seeds": sorted(staged, key=lambda x: int(x)),
                "overlap": sorted(active & staged, key=lambda x: int(x)),
            })
    return mismatches


def do_scan():
    ensemble_config = read_ensemble_config()
    staged_models = scan_staged_models()

    snapshot = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "machine": machine_tag(),
        "repo_root": str(REPO_ROOT),
        "staging": {
            "exists": STAGING.exists(),
            "staged_models_by_ticker": staged_models,
            "staging_src_modules": scan_staging_src(),
            "ensemble_config": ensemble_config,
            "ready_flag_present": (STAGING / "STAGING_READY.md").exists(),
        },
        "production_models": scan_production_models(),
        "experiment_snapshots": scan_snapshot_leaderboards(),
        "fork_b": scan_fork_b(),
        "active_seed_mismatches": find_active_seed_mismatches(ensemble_config, staged_models),
    }

    out_path = REPO_ROOT / f"state_snapshot_{machine_tag()}.json"
    out_path.write_text(json.dumps(snapshot, indent=2))
    print(f"Wrote {out_path}")
    print(f"  Staged tickers: {list(staged_models.keys())}")
    print(f"  Production models/: {snapshot['production_models'].get('count', 0)} files")
    print(f"  Experiment snapshot files: {snapshot['experiment_snapshots']['count']}")
    if snapshot["active_seed_mismatches"]:
        print(f"  ⚠ Active-seed mismatches: {[m['ticker'] for m in snapshot['active_seed_mismatches']]}")


def _file_set(section):
    """Extract {filename: size_bytes} from a scan section with a 'files' list."""
    return {f["file"]: f.get("size_bytes") for f in section.get("files", [])}


def do_compare(path_a: Path, path_b: Path):
    a = json.loads(path_a.read_text())
    b = json.loads(path_b.read_text())
    name_a, name_b = a.get("machine", "A"), b.get("machine", "B")

    print(f"=== Comparing {name_a}  vs  {name_b} ===\n")

    # --- experiment_snapshots ---
    snap_a, snap_b = a["experiment_snapshots"], b["experiment_snapshots"]
    print(f"experiment_snapshots: {name_a}={snap_a['count']}  {name_b}={snap_b['count']}"
          f"  {'✓ match' if snap_a['count'] == snap_b['count'] else '✗ MISMATCH'}")
    fa, fb = _file_set(snap_a), _file_set(snap_b)
    only_a = set(fa) - set(fb)
    only_b = set(fb) - set(fa)
    if only_a:
        print(f"  Files only on {name_a} ({len(only_a)}): {sorted(only_a)[:5]}{' ...' if len(only_a) > 5 else ''}")
    if only_b:
        print(f"  Files only on {name_b} ({len(only_b)}): {sorted(only_b)[:5]}{' ...' if len(only_b) > 5 else ''}")

    # --- production models/ ---
    print()
    pm_a, pm_b = a.get("production_models", {}), b.get("production_models", {})
    ca, cb = pm_a.get("count", 0), pm_b.get("count", 0)
    print(f"production_models/: {name_a}={ca}  {name_b}={cb}"
          f"  {'✓ match' if ca == cb else '✗ MISMATCH'}")
    pfa, pfb = _file_set(pm_a), _file_set(pm_b)
    only_a, only_b = set(pfa) - set(pfb), set(pfb) - set(pfa)
    if only_a:
        print(f"  Only on {name_a}: {sorted(only_a)}")
    if only_b:
        print(f"  Only on {name_b}: {sorted(only_b)}")
    common = set(pfa) & set(pfb)
    size_diffs = [f for f in common if pfa[f] != pfb[f]]
    if size_diffs:
        print(f"  Size mismatches on shared files: {size_diffs}")

    # --- staged models ---
    print()
    staged_a = a["staging"]["staged_models_by_ticker"]
    staged_b = b["staging"]["staged_models_by_ticker"]
    tickers = sorted(set(staged_a) | set(staged_b))
    print("staged_models_by_ticker:")
    for t in tickers:
        seeds_a = sorted(s["seed"] for s in staged_a.get(t, []))
        seeds_b = sorted(s["seed"] for s in staged_b.get(t, []))
        status = "✓" if seeds_a == seeds_b else "✗ DIFFERS"
        print(f"  {t}: {name_a}={seeds_a}  {name_b}={seeds_b}  {status}")

    # --- ensemble_config ---
    print()
    cfg_a = a["staging"]["ensemble_config"] or {}
    cfg_b = b["staging"]["ensemble_config"] or {}
    same_cfg = cfg_a == cfg_b
    print(f"ensemble_config.json: {'✓ identical' if same_cfg else '✗ DIFFERS'}")
    if not same_cfg:
        for t in sorted(set(cfg_a) | set(cfg_b)):
            if cfg_a.get(t) != cfg_b.get(t):
                print(f"  {t} differs — {name_a}: {cfg_a.get(t)}")
                print(f"  {t} differs — {name_b}: {cfg_b.get(t)}")

    # --- active seed mismatches (within each machine) ---
    print()
    for label, snap in ((name_a, a), (name_b, b)):
        mismatches = snap.get("active_seed_mismatches", [])
        if mismatches:
            print(f"⚠ {label}: active_seeds vs staged mismatch on "
                  f"{[m['ticker'] for m in mismatches]}")
        else:
            print(f"✓ {label}: no active-seed/staged mismatches")

    print("\n=== End comparison ===")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--compare", nargs=2, metavar=("SNAPSHOT_A", "SNAPSHOT_B"))
    args = parser.parse_args()

    if args.compare:
        do_compare(Path(args.compare[0]), Path(args.compare[1]))
    else:
        do_scan()


if __name__ == "__main__":
    main()