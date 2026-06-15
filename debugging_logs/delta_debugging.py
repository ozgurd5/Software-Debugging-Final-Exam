"""
Delta debugging / input minimization (Question 5) -- evidence.

A systematic greedy minimizer.
  Phase 1: repeatedly try to delete each element (every key, at any depth) of the parsed config and
           keep a deletion only when the failure (the crash) still occurs; repeat until no single
           deletion preserves the failure.
  Phase 2: confirm the result is "1-minimal" -- deleting ANY one remaining element makes the failure
           disappear, so nothing more can be removed.
Pass/fail is decided by the Question 2 oracle. Re-run from the project root with:
    py debugging_logs/delta_debugging.py
"""
import copy
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from tests.oracle import is_failure


def removable_paths(node, prefix=()):
    """Return the key-path of every key in every nested dict (parents before children)."""
    paths = []
    if isinstance(node, dict):
        for key in node:
            path = prefix + (key,)
            paths.append(path)
            paths.extend(removable_paths(node[key], path))
    return paths


def without(config, path):
    """Return a deep copy of config with the element at key-path `path` deleted."""
    trial = copy.deepcopy(config)
    parent = trial
    for key in path[:-1]:
        parent = parent[key]
    del parent[path[-1]]
    return trial


def outcome(config):
    """'failure' if the crash still occurs, otherwise 'no failure'."""
    return "failure" if is_failure(config) else "no failure"


def minimize(config):
    """Delete any element whose removal keeps the failure; repeat until none can be removed."""
    step = 0
    changed = True
    while changed:
        changed = False
        for path in removable_paths(config):
            trial = without(config, path)
            if is_failure(trial):
                config = trial
                step += 1
                print(f"  step {step:2}: remove {'.'.join(path):26} -> failure remains  (KEEP)")
                changed = True
                break
    return config


def confirm_minimal(config):
    """Show 1-minimality: removing any single remaining element makes the failure disappear."""
    for path in removable_paths(config):
        print(f"  remove {'.'.join(path):16} -> {outcome(without(config, path)):11} -> essential, kept")


def main():
    original = json.loads((ROOT / "inputs" / "large_config_failure.json").read_text(encoding="utf-8"))
    print("original ->", outcome(original))

    print("\nPhase 1 -- greedy reduction (one element per step):")
    minimal = minimize(original)

    print("\nminimal failure-inducing input:")
    print(json.dumps(minimal, indent=2))

    print("\nPhase 2 -- 1-minimality check (each remaining element is essential):")
    confirm_minimal(minimal)


if __name__ == "__main__":
    main()
