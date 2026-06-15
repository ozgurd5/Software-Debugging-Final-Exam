# JSON Config Parser — Systematic Debugging

This repository contains the take-home final for the **"Software Debugging"** course: a deliberately
faulty JSON configuration parser that is investigated and fixed end-to-end with systematic debugging
techniques rather than ad-hoc patching.

The defect lives in `parse_bool()`, which assumes every non-boolean value is string-like and calls
`.lower()` on it — so a JSON `null` (Python `None`), or an `int` / `list` / `float`, crashes the parser
with an uncaught `AttributeError` instead of being rejected with a clean `ConfigError`. The project
reproduces this failure, builds a test oracle around it, and then narrows it down with scientific
debugging, delta debugging, runtime tracing, program slicing and the defect–infection–failure chain,
finishing with a root-cause patch, a regression test and mutation testing.

## 📂 Table of Contents and File Descriptions

### 1. The Parser (`src/`)
The program under investigation.
* **`config_parser.py`** — loads, validates and normalizes a config into `server`, `features`, `limits`
  and `logging`. Holds the defect in `parse_bool` and its root-cause fix (a type guard that rejects
  non-string values with a clean `ConfigError`).
* **`app.py`** — the command-line entry point: prints `CONFIG_OK` (exit code 0) or `CONFIG_ERROR: ...`
  (exit code 1).

### 2. Sample Inputs (`inputs/`)
* **`valid_basic.json`**, **`valid_full.json`** — well-formed configs that normalize successfully.
* **`large_config_failure.json`** — the failure-inducing input (`"debug": null`) that triggers the bug.

### 3. Tests (`tests/`)
* **`oracle.py`** — the test oracle `is_failure()`: an uncontrolled crash is a *failure*, while a clean
  `ConfigError` or a normal result is *expected* (so the fix can be validated).
* **`test_config_cases.py`** — passing and failing tests covering defaults, alternative boolean
  spellings, validation, and the four type-handling bug cases.
* **`test_regression.py`** — the regression guard: the minimal failing input must stay a controlled
  `ConfigError`, never crash again.
* **`test_config_parser.py`** — the bundled starter tests (left untouched).

### 4. Debugging Evidence (`debugging_logs/`)
Runnable scripts and their captured `.md` outputs, one per technique:
* **`hypothesis_experiments.py`** — scientific debugging: four hypotheses, each tested by changing one
  variable on the real failing input.
* **`delta_debugging.py`** — input minimization down to the 1-minimal failure-inducing input.
* **`trace_run.py`** — a runtime execution trace produced by wrapping the parser's functions at runtime
  (the source is never modified).
* **`mutation_test.py`** — mutation testing: applies small code mutations and measures how many the test
  suite catches.
* **`test_results.md`** — the full test suite before and after the fix (red → green).

### 5. Report (`report.md`)
The full debugging report: environment, failure reproduction, the test oracle, the test suite,
scientific debugging, delta debugging, tracing, program slicing, the defect–infection–failure chain,
the patch, validation, and the two bonuses (regression test and mutation testing).

## 🚀 Installation and Execution

Requirements: **Python 3.10+** and **pytest**.

```bash
pip install pytest
```

Run the application on the sample configs:

```bash
python src/app.py inputs/valid_basic.json            # CONFIG_OK
python src/app.py inputs/valid_full.json             # CONFIG_OK
python src/app.py inputs/large_config_failure.json   # CONFIG_ERROR (clean, after the fix)
```

Run the test suite:

```bash
pytest -q
```

Run the debugging scripts from the project root:

```bash
python debugging_logs/hypothesis_experiments.py   # scientific debugging
python debugging_logs/delta_debugging.py          # input minimization
python debugging_logs/trace_run.py                # runtime trace
python debugging_logs/mutation_test.py            # mutation testing
```
