"""
Trace / logging analysis (Question 6) -- evidence.

Replaces the parser's functions with thin tracing wrappers at runtime (the instructor's source is
untouched) to log what happens while inputs/large_config_failure.json is processed, then catches the
crash and reports the state right before it.
Re-run from the project root with:  py debugging_logs/trace_run.py
"""
import sys
import traceback
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import src.config_parser as cp

# Keep the originals, then install flat tracing wrappers (no nested functions).
original_normalize_server = cp.normalize_server
original_normalize_features = cp.normalize_features
original_parse_bool = cp.parse_bool


def log_section(name, section):
    print(f"[section]    processing '{name}'  (keys = {list(section)})")


def traced_normalize_server(section):
    log_section("server", section)
    return original_normalize_server(section)


def traced_normalize_features(section):
    log_section("features", section)
    return original_normalize_features(section)


def traced_parse_bool(value):
    ok = isinstance(value, (bool, str))
    note = "" if ok else "   <-- NOT bool/str: unexpected type!"
    print(f"[parse_bool]  value={value!r}  type={type(value).__name__}{note}")
    return original_parse_bool(value)


def main():
    cp.normalize_server = traced_normalize_server
    cp.normalize_features = traced_normalize_features
    cp.parse_bool = traced_parse_bool

    path = ROOT / "inputs" / "large_config_failure.json"
    print(f"load_config('{path.name}')\n")
    try:
        cp.load_config(path)
        print("\nresult: CONFIG_OK")
    except cp.ConfigError as exc:
        print(f"\nresult: ConfigError (controlled) -> {exc}")
    except Exception as exc:
        frame = traceback.extract_tb(sys.exc_info()[2])[-1]
        print(f"\n!! CRASH: {type(exc).__name__}: {exc}")
        print(f"   right before crash: {frame.name}() at {Path(frame.filename).name}:{frame.lineno}")
        print(f"   crashing line: {frame.line}")


if __name__ == "__main__":
    main()
