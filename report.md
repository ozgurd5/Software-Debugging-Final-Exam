# Debugging Report

## 1. Project and Environment

- Student name: Özgür Dalbeler
- Student number: 2022280084
- Python version: 3.13.2
- Operating system: Windows 10 Pro (build 10.0.19045)
- Date: 13/06/2026

---

## 2. Failure Reproduction

### Command

Run from the project root:

```bash
python src/app.py inputs/large_config_failure.json
```

### Observed failure

Instead of printing `CONFIG_OK` or a clean `CONFIG_ERROR`, the program terminates with an
uncaught exception and exit code 1:

```text
Traceback (most recent call last):
  File "src/app.py", line 23, in <module>
    raise SystemExit(main())
  File "src/app.py", line 13, in main
    config = load_config(path)
  File "src/config_parser.py", line 16, in load_config
    return normalize_config(raw_config)
  File "src/config_parser.py", line 24, in normalize_config
    features = normalize_features(config.get("features", {}))
  File "src/config_parser.py", line 73, in normalize_features
    debug = parse_bool(features.get("debug", False))
  File "src/config_parser.py", line 150, in parse_bool
    lowered = value.lower()
              ^^^^^^^^^^^
AttributeError: 'NoneType' object has no attribute 'lower'
```

### Failure type

**Crash** (uncaught `AttributeError`). `app.py` only catches `ConfigError` (line 17); the
exception raised here is an `AttributeError`, so it is not caught, propagates to the top level,
and ends the program with a traceback and a non-zero exit code. This is not a "wrong output"
case — the program produces neither `CONFIG_OK` nor a clean `CONFIG_ERROR`. It can also be
described as "unexpected behavior," since a well-designed parser should reject an invalid
boolean with a clean `ConfigError` instead of crashing.

**Reproducibility.** The failure is fully deterministic: every run fails at the same line
(`config_parser.py:150`, inside `parse_bool`) with the same traceback. It depends only on the
contents of the input file — there is no randomness, timing, or external state. The other two
inputs always succeed, so the input file is the single independent variable and the failure is
reliably reproducible:

| Input | Output | Exit code |
|---|---|---|
| `inputs/valid_basic.json` | `CONFIG_OK` | 0 |
| `inputs/valid_full.json` | `CONFIG_OK` | 0 |
| `inputs/large_config_failure.json` | `AttributeError` (crash) | 1 |

---

## 3. Test Oracle

The oracle treats an execution as **expected (pass)** when `normalize_config()` either returns a
normalized dictionary or raises a clean `ConfigError` (the parser's designed way to reject invalid
input). It reports a **failure** only when some *other* exception escapes `normalize_config()` — an
uncontrolled crash such as the `AttributeError` from `parse_bool(None)`, which `app.py`'s
`except ConfigError` cannot catch. The oracle lives in `tests/oracle.py` and is reused by the tests
in Section 4.

```python
from src.config_parser import normalize_config, ConfigError

def is_failure(raw_config):
    try:
        normalize_config(raw_config)
    except ConfigError:
        return False   # controlled rejection -> expected
    except Exception:
        return True    # uncontrolled crash -> FAILURE
    return False       # normalized successfully -> expected
```

At the program level this maps to: PASS = exit code 0 (`CONFIG_OK`) or exit code 1 with a
`CONFIG_ERROR:` message; FAIL = the process aborts with an uncaught traceback.

---

## 4. Passing and Failing Tests

The tests live in `tests/test_config_cases.py` (the bundled `tests/test_config_parser.py` is left
untouched). They deliberately exercise *different* checks from the bundled suite — logging-level and
section-type validation, alternative boolean spellings, the oracle, and four bug cases — rather than
repeating it. Current run — **11 passed, 4 failed**. The four failing tests assert the *correct*
behaviour (a clean `ConfigError`) and are red only because of the bug; they turn green after the
patch (Section 10), as shown in Section 11.

| Test name | Input summary | Expected result | Actual result | Pass/Fail |
|---|---|---|---|---|
| test_valid_minimal_defaults | empty server/features/limits | normalized dict with defaults (port 8080, level INFO, ...) | as expected | Pass |
| test_alternative_string_booleans | features cache="1", debug="0", experimental="yes" | True, False, True | as expected | Pass |
| test_real_booleans_passthrough | features cache=true, debug=false | cache=True, debug=False | as expected | Pass |
| test_oracle_marks_valid_config_as_expected | a valid config dict (via oracle) | is_failure → False | False | Pass |
| test_invalid_logging_level_raises_config_error | logging.level = "VERBOSE" | ConfigError | ConfigError | Pass |
| test_non_object_section_raises_config_error | server = "localhost" (string, not object) | ConfigError | ConfigError | Pass |
| test_null_debug_raises_config_error | features.debug = null | ConfigError (clean reject) | AttributeError ('NoneType' has no 'lower') | **Fail** |
| test_int_boolean_raises_config_error | features.cache = 1 (int) | ConfigError | AttributeError ('int' has no 'lower') | **Fail** |
| test_list_boolean_raises_config_error | features.experimental = [] (list) | ConfigError | AttributeError ('list' has no 'lower') | **Fail** |
| test_large_config_file_raises_config_error | real inputs/large_config_failure.json (debug=null) | ConfigError | AttributeError crash (config_parser.py:150) | **Fail** |

---

## 5. Scientific Debugging

| Hypothesis | Observation | Experiment | Result | Accepted/Rejected |
|---|---|---|---|---|
| H1 | | | | |
| H2 | | | | |
| H3 | | | | |

---

## 6. Delta Debugging / Input Minimization

### Original input size

### Reduction steps

| Step | Change attempted | Did failure remain? | Conclusion |
|---|---|---|---|
| 1 | | | |
| 2 | | | |
| 3 | | | |

### Minimal or near-minimal failure-inducing input

```json

```

---

## 7. Trace / Logging Analysis

Relevant trace:

```text

```

Interpretation:

---

## 8. Program Slicing / Dependency Analysis

### Critical variable

### Input field affecting it

### Relevant functions

### Relevant lines

### Explanation

---

## 9. Defect–Infection–Failure Chain

### Defect

### Infection

### Propagation

### Failure

---

## 10. Patch

### Changed file/function

### Explanation

### Patch summary

```diff

```

---

## 11. Validation

Show that tests pass after your fix.

```bash

```

---

## 12. Bonus: Regression Test

Optional.

---

## 13. Bonus: Mutation Testing

Optional.

| Mutant | Change | Killed? | Explanation |
|---|---|---|---|
| | | | |
