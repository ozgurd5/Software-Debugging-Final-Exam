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
* **`config_parser.py`** — loads, validates and normalizes a config into `server`, `features`, `limits`
  and `logging`. Holds the defect in `parse_bool` and its root-cause fix (a type guard that rejects
  non-string values with a clean `ConfigError`).
* **`app.py`** — the command-line entry point: prints `CONFIG_OK` (exit code 0) or `CONFIG_ERROR: ...`
  (exit code 1).

### 2. Sample Inputs (`inputs/`)
* **`valid_basic.json`**, **`valid_full.json`** — well-formed configs that normalize successfully.
* **`large_config_failure.json`** — the failure-inducing input (`"debug": null`) that triggers the bug.

### 3. Tests (`tests/`)
* **`oracle.py`** — the test oracle `is_failure()`: an uncontrolled crash is a *failure*, a clean
  `ConfigError` or a normal result is *expected*.
* **`test_config_cases.py`** — passing/failing tests: defaults, alternative boolean spellings,
  validation, and the four type-handling bug cases.
* **`test_regression.py`** — the regression guard (Bonus A): the minimal failing input must stay a
  controlled `ConfigError`.
* **`test_config_parser.py`** — the bundled starter tests (left untouched).

### 4. Debugging Evidence (`debugging_logs/`)
Each technique has a runnable script and a captured `.md` output:
* **`hypothesis_experiments.py`** + **`hypothesis_experiments_output.md`** — scientific debugging (four
  hypotheses, one variable each).
* **`delta_debugging.py`** + **`delta_debugging_output.md`** — input minimization to the 1-minimal
  failure-inducing input.
* **`trace_run.py`** + **`trace_output.md`** — a runtime trace produced by wrapping the parser's
  functions (the source is never modified).
* **`mutation_test.py`** + **`mutation_output.md`** — mutation testing (test-suite quality).
* **`test_results.md`** — the full test suite before vs after the fix (red → green).

### 5. Report and Written Answers
* **`report.md`** — the full debugging report in **English** (the primary deliverable; 13 sections).
* **`exam_answers.md`** — the answers for the hand-written exam paper, in **Turkish**, at the same depth
  as the report.
* **`question_explanations.md`** — detailed concept and learning notes per question, in **Turkish**.

### 6. Course Material and Tooling
* **`FINAL_QUESTION.md`** — the exam questions (9 + 2 bonuses).
* **`Yazilimlarda_Hata_Ayiklama_TakeHome_Final_Sinav_Kagidi.docx.md`** — the official exam paper
  (Turkish), converted to Markdown.
* **`docs/`** — the instructor's `report_template.md` and grading `rubric.md`.
* **`.README_DEFAULT.md`** — the original starter README shipped with the assignment.
* **`requirements.txt`** — Python dependencies (`pytest`).
* **`make_submission.ps1`** — builds the flat submission `.zip`.
* **`CLAUDE.md`** — project memory and working rules used during development.

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
