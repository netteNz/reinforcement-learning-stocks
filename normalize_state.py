import json
import csv
from pathlib import Path
from datetime import datetime, timezone
import socket

REPO_ROOT = Path(__file__).resolve().parent
STAGING = REPO_ROOT / "staging"
SNAPSHOTS = REPO_ROOT / "data" / "experiment_snapshots"

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
                "modified": datetime.fromtimestamp(
                    f.stat().st_mtime, tz=timezone.utc
                ).isoformat(),
            })
        result[ticker_dir.name.upper()] = seeds
    return result

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
    """data/experiment_snapshots/*.csv -> per-file row count + latest per ticker prefix"""
    if not SNAPSHOTS.exists():
        return {"exists": False, "count": 0, "files": []}
    files = list(SNAPSHOTS.glob("*.csv"))
    summary = []
    for f in sorted(files):
        try:
            with f.open(newline="", encoding="utf-8", errors="replace") as fh:
                row_count = sum(1 for _ in csv.reader(fh)) - 1  # minus header
        except Exception as e:
            row_count = None
        summary.append({
            "file": f.name,
            "rows": row_count,
            "size_bytes": f.stat().st_size,
            "modified": datetime.fromtimestamp(
                f.stat().st_mtime, tz=timezone.utc
            ).isoformat(),
        })
    return {"exists": True, "count": len(files), "files": summary}

def scan_fork_b():
    result = {}
    for opt in ("fork_b_option1_snapshots", "fork_b_option2_snapshots"):
        d = REPO_ROOT / "data" / opt
        result[opt] = sorted(f.name for f in d.glob("*")) if d.exists() else None
    return result

def main():
    snapshot = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "machine": machine_tag(),
        "repo_root": str(REPO_ROOT),
        "staging": {
            "exists": STAGING.exists(),
            "staged_models_by_ticker": scan_staged_models(),
            "staging_src_modules": scan_staging_src(),
            "ensemble_config": read_ensemble_config(),
            "ready_flag_present": (STAGING / "STAGING_READY.md").exists(),
        },
        "experiment_snapshots": scan_snapshot_leaderboards(),
        "fork_b": scan_fork_b(),
    }

    out_path = REPO_ROOT / f"state_snapshot_{machine_tag()}.json"
    out_path.write_text(json.dumps(snapshot, indent=2))
    print(f"Wrote {out_path}")
    print(f"  Staged tickers: {list(snapshot['staging']['staged_models_by_ticker'].keys())}")
    print(f"  Experiment snapshot files: {snapshot['experiment_snapshots']['count']}")

if __name__ == "__main__":
    main()