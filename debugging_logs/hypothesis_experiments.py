"""
Scientific debugging experiments (Question 4) -- evidence.

Each experiment starts from the real failing input (inputs/large_config_failure.json)
and changes exactly one thing, isolating what triggers the crash. Re-run from the
project root with:  py debugging_logs/hypothesis_experiments.py

The bundled inputs/*.json files are NOT modified; every variant is built in memory
from a fresh deep copy of the real file.
"""
import copy
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.config_parser import normalize_config, ConfigError

REAL = json.loads((ROOT / "inputs" / "large_config_failure.json").read_text(encoding="utf-8"))


def outcome(raw):
    try:
        normalize_config(raw)
        return "OK (normalized)"
    except ConfigError:
        return "ConfigError (controlled)"
    except Exception as exc:
        return "CRASH: " + type(exc).__name__


def real_copy():
    return copy.deepcopy(REAL)


def main():
    experiments = []

    # H1 -- does a JSON null in a boolean field trigger the crash? (change only features.debug)
    experiments.append(("H1", "real file as-is (debug=null)", real_copy()))
    cfg = real_copy(); cfg["features"]["debug"] = False
    experiments.append(("H1", "real file, debug=false (control)", cfg))

    # H2 -- null-specific, or any non-bool/non-string type? (set features.debug to int/list/float)
    for label, value in [("int 1", 1), ("list []", []), ("float 1.5", 1.5)]:
        cfg = real_copy(); cfg["features"]["debug"] = value
        experiments.append(("H2", f"real file, debug={label}", cfg))

    # H3 -- is a missing required section the cause? (remove 'limits')
    cfg = real_copy(); del cfg["limits"]
    experiments.append(("H3", "real file minus 'limits'", cfg))

    # H4 -- is the large/nested structure the cause? (strip nested vs. fix the value)
    cfg = real_copy()
    for key in ("services", "security", "metadata"):
        cfg.pop(key, None)
    experiments.append(("H4", "real file, nested removed (debug=null)", cfg))
    cfg = real_copy(); cfg["features"]["debug"] = False
    experiments.append(("H4", "real file, nested kept, debug=false", cfg))

    for tag, description, cfg in experiments:
        print(f"{tag}  {description:40} -> {outcome(cfg)}")


if __name__ == "__main__":
    main()
