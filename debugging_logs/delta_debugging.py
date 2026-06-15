"""
Delta debugging / input minimization (Question 5) -- evidence.

A single annotated greedy pass over every element (each key, at any depth) of the parsed config:
delete the element and keep the deletion if the crash still occurs (REMOVED -- the element is
irrelevant); otherwise leave it in place (ESSENTIAL -- removing it changes the outcome). What remains
is the minimal failure-inducing input, and the ESSENTIAL rows are exactly its irreducible core.
The crash / no-crash decision is the Question 2 oracle. Re-run from the project root with:
    py debugging_logs/delta_debugging.py
"""
import copy
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.config_parser import ConfigError, normalize_config
from tests.oracle import is_failure


def removable_paths(node, prefix=()):
    """Key-path of every key in every nested dict (parents before children)."""
    paths = []
    if isinstance(node, dict):
        for key in node:
            path = prefix + (key,)
            paths.append(path)
            paths.extend(removable_paths(node[key], path))
    return paths


def contains(config, path):
    """True if `path` still exists (its parent was not already removed earlier in the pass)."""
    node = config
    for key in path:
        if not isinstance(node, dict) or key not in node:
            return False
        node = node[key]
    return True


def without(config, path):
    """Deep copy of config with the element at `path` deleted."""
    trial = copy.deepcopy(config)
    parent = trial
    for key in path[:-1]:
        parent = parent[key]
    del parent[path[-1]]
    return trial


def describe(config):
    """Why an essential deletion is rejected: a controlled error or a clean normalization."""
    try:
        normalize_config(config)
        return "normalizes OK"
    except ConfigError:
        return "clean ConfigError"
    except Exception as exc:
        return f"CRASH ({type(exc).__name__})"


def minimize(config):
    """One annotated pass: delete each element, keeping the deletion only if the crash survives."""
    for path in removable_paths(config):
        if not contains(config, path):
            continue
        trial = without(config, path)
        name = ".".join(path)
        if is_failure(trial):
            config = trial
            print(f"  delete {name:25} -> {'still crashes':17} -> REMOVED")
        else:
            print(f"  delete {name:25} -> {describe(trial):17} -> ESSENTIAL")
    return config


def main():
    config = json.loads((ROOT / "inputs" / "large_config_failure.json").read_text(encoding="utf-8"))
    print("original ->", "failure" if is_failure(config) else "no failure")
    print("\nGreedy pass -- delete each element; keep the deletion only if the crash survives:")
    minimal = minimize(config)
    print("\nminimal failure-inducing input:")
    print(json.dumps(minimal, indent=2))


if __name__ == "__main__":
    main()
