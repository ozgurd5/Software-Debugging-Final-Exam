"""
Mutation testing (Bonus B) -- evidence.

Applies small mutations to src/config_parser.py one at a time, runs the full test suite against each
mutant, and reports whether the suite KILLS it (some test fails) or it SURVIVES (all tests pass -- a
gap in the suite). The original source is restored after every mutant and on exit. The baseline must
be green first. Run from the project root with the venv interpreter (it has pytest):
    .venv\\Scripts\\python.exe debugging_logs/mutation_test.py
"""
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src" / "config_parser.py"

# (label, description, original snippet, mutated snippet)
MUTANTS = [
    ("M1", "parse_bool: drop the non-string guard (reverts the fix)",
     '    if not isinstance(value, str):\n        raise ConfigError(f"Invalid boolean value: {value}")\n\n    lowered = value.lower()',
     '    lowered = value.lower()'),
    ("M2", 'parse_bool: drop "1" from the accepted true values',
     '    if lowered in ["true", "yes", "1"]:',
     '    if lowered in ["true", "yes"]:'),
    ("M3", 'normalize_logging: also accept "VERBOSE" as a valid level',
     '    if level not in ["DEBUG", "INFO", "WARNING", "ERROR"]:',
     '    if level not in ["DEBUG", "INFO", "WARNING", "ERROR", "VERBOSE"]:'),
    ("M4", "validate_required_sections: invert the presence check (not in -> in)",
     '        if section not in config:',
     '        if section in config:'),
    ("M5", "normalize_server: weaken the port upper bound (> -> >=)",
     '    if port <= 0 or port > 65535:',
     '    if port <= 0 or port >= 65535:'),
    ("M6", "normalize_features: change the cache default (False -> True)",
     '    cache = parse_bool(features.get("cache", False))',
     '    cache = parse_bool(features.get("cache", True))'),
]


def suite_passes():
    """True if the whole test suite passes (mutant survives); False if a test fails (killed)."""
    result = subprocess.run(
        [sys.executable, "-m", "pytest", "-q", "--tb=no"],
        cwd=ROOT, capture_output=True, text=True,
    )
    return result.returncode == 0


def main():
    original = SRC.read_text(encoding="utf-8")
    print("baseline (no mutation) ->", "all tests pass" if suite_passes() else "FAIL (cannot mutate)")
    print("\nMutants (KILLED = suite caught it; SURVIVED = gap in the tests):")
    killed = 0
    try:
        for label, desc, find, replace in MUTANTS:
            if find not in original:
                print(f"  {label}  NOT-FOUND  {desc}")
                continue
            SRC.write_text(original.replace(find, replace, 1), encoding="utf-8")
            survived = suite_passes()
            SRC.write_text(original, encoding="utf-8")
            status = "SURVIVED" if survived else "KILLED"
            if not survived:
                killed += 1
            print(f"  {label}  {status:8}  {desc}")
    finally:
        SRC.write_text(original, encoding="utf-8")
    print(f"\nmutation score: {killed}/{len(MUTANTS)} killed")


if __name__ == "__main__":
    main()
