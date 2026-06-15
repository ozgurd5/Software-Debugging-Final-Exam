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
repeating it. Current run — **11 passed, 4 failed** (full before-fix output: `debugging_logs/test_results.md`). The four failing tests assert the *correct*
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

Each hypothesis was tested with a **controlled experiment**: start from the real failing input
`inputs/large_config_failure.json` and change exactly one thing, observing the outcome (normalizes
OK / clean `ConfigError` / uncontrolled crash). The experiments are runnable in
`debugging_logs/hypothesis_experiments.py`; their captured output:

```text
H1  real file as-is (debug=null)             -> CRASH: AttributeError
H1  real file, debug=false (control)         -> OK (normalized)
H2  real file, debug=int 1                   -> CRASH: AttributeError
H2  real file, debug=list []                 -> CRASH: AttributeError
H2  real file, debug=float 1.5               -> CRASH: AttributeError
H3  real file minus 'limits'                 -> ConfigError (controlled)
H4  real file, nested removed (debug=null)   -> CRASH: AttributeError
H4  real file, nested kept, debug=false      -> OK (normalized)
```

| Hypothesis | Observation | Experiment | Result | Accepted/Rejected |
|---|---|---|---|---|
| **H1** — A JSON `null` (Python `None`) in a boolean field triggers the failure. | The crash is an `AttributeError` from `.lower()`, a method only strings have; in the failing file `features.debug` is the one field whose value (`null`) has no string form, while every other value is a normal string/int/bool. That singles out the `null`. | Run the file as-is (`debug: null`); then run it again changing **only** `features.debug` to `false`. | As-is → uncaught `AttributeError` (crash); with `false` → normalizes and exits 0. One field flips crash↔success, so the `null` value is the trigger. | **Accepted** |
| **H2** — The trigger is not `null`-specific: **any** non-bool, non-string value (int, list, float) crashes the same way. | `parse_bool` special-cases only `bool`, then calls `value.lower()` unconditionally — nothing there is specific to `null`; it is simply not a string, and neither are ints, floats or lists. | On the real file set `features.debug` to `1` (int), then `[]` (list), then `1.5` (float) — one type per run. | All three crash identically: `AttributeError: '<type>' object has no attribute 'lower'`. The trigger is any non-bool, non-string value, not `null` alone. | **Accepted** |
| **H3** — The failure is caused by a **missing** required section, not by a bad value. | There is only one failing input and it differs from the passing files in many ways at once; the rival "a required section is missing" must be eliminated before crediting the value. | Remove the entire `limits` section from the real file and run. | A clean `ConfigError: Missing required section: limits` (exit 1, no traceback) — a controlled rejection, not a crash. A missing section is handled correctly, so it is not the cause. | **Rejected** |
| **H4** — The failure is caused by the large / deeply-nested structure (`services`, `security`, `metadata`, ...). | The failing file is ~60 lines and deeply nested while the passing files are small and flat — a size/nesting confound that must be controlled for before blaming the value. | Two runs: (a) strip the nested sections but keep `debug: null`; (b) keep all nesting but set `debug: false`. | (a) still crashes; (b) normalizes cleanly. The outcome tracks the `debug` value, not the structure — the parser never even inspects those sections. | **Rejected** |

Conclusion: the crash is caused by `parse_bool` calling `.lower()` on a non-string value — narrowed by
H1 (the `null` in `features.debug`) and generalised by H2 (any non-bool, non-string value). It is
**independent** of missing sections (H3) and of the large/nested structure (H4).

---

## 6. Delta Debugging / Input Minimization

### Original input size

`inputs/large_config_failure.json`: ≈61 lines, 7 top-level sections (`metadata`, `server`,
`features`, `limits`, `logging`, `services`, `security`); `features` alone has 5 keys.

### Reduction steps

A **single annotated greedy pass** (`debugging_logs/delta_debugging.py`, run on the original buggy
parser) deletes each element — every key, at any depth — in turn: keep the deletion if the crash still
occurs (**REMOVED**, the element is irrelevant), otherwise leave the element in place (**ESSENTIAL**,
removing it changes the outcome). The crash / no-crash decision is the Question 2 oracle
(`tests/oracle.is_failure`). The table below **is** the full trace; the ESSENTIAL rows are the
irreducible core, so the result is 1-minimal — deleting any one of them makes the crash disappear.

| # | Delete | Outcome | Decision |
|---|---|---|---|
| 1 | `metadata` | still crashes | REMOVED |
| 2 | `server` | clean `ConfigError` | **ESSENTIAL** (kept) |
| 3 | `server.host` | still crashes | REMOVED |
| 4 | `server.port` | still crashes | REMOVED |
| 5 | `features` | clean `ConfigError` | **ESSENTIAL** (kept) |
| 6 | `features.cache` | still crashes | REMOVED |
| 7 | `features.debug` | normalizes OK | **ESSENTIAL** (the trigger) |
| 8 | `features.experimental` | still crashes | REMOVED |
| 9 | `features.recommendations` | still crashes | REMOVED |
| 10 | `features.new_checkout` | still crashes | REMOVED |
| 11 | `limits` | clean `ConfigError` | **ESSENTIAL** (kept) |
| 12 | `limits.max_users` | still crashes | REMOVED |
| 13 | `limits.timeout` | still crashes | REMOVED |
| 14 | `limits.retries` | still crashes | REMOVED |
| 15 | `logging` | still crashes | REMOVED |
| 16 | `services` | still crashes | REMOVED |
| 17 | `security` | still crashes | REMOVED |

### Minimal or near-minimal failure-inducing input

```json
{
  "server": {},
  "features": {
    "debug": null
  },
  "limits": {}
}
```

**Why this input still fails.** `server`, `features` and `limits` must all be present, otherwise
`validate_required_sections` raises a clean `ConfigError` (the ESSENTIAL rows above) — a different
outcome, not the crash. With all three present, `normalize_features` calls `parse_bool(features["debug"])` =
`parse_bool(None)`, which executes `None.lower()` → `AttributeError`. The `null` boolean value is the
single irreducible trigger; everything else in the original file is noise.

---

## 7. Trace / Logging Analysis

The trace was produced by `debugging_logs/trace_run.py`, which wraps the parser's functions at runtime
(the source is not modified) and logs each section/field as it is processed, then reports the state at
the crash. Full output: `debugging_logs/trace_output.md`.

Relevant trace:

```text
load_config('large_config_failure.json')

[section]    processing 'server'  (keys = ['host', 'port'])
[section]    processing 'features'  (keys = ['cache', 'debug', 'experimental', 'recommendations', 'new_checkout'])
[parse_bool]  value=True  type=bool
[parse_bool]  value=None  type=NoneType   <-- NOT bool/str: unexpected type!

!! CRASH: AttributeError: 'NoneType' object has no attribute 'lower'
   right before crash: parse_bool() at config_parser.py:150
   crashing line: lowered = value.lower()
```

Interpretation:

- **Sections processed:** `normalize_config` handles `server`, `features`, `limits`, `logging` in that
  order; `metadata`, `services` and `security` are ignored (never read). Here `server` is normalized
  successfully and `features` begins; the crash occurs inside `features`, so `limits` and `logging` are
  never reached.
- **Fields normalized:** before `features`, `normalize_server` reads and validates `server.host` and
  `server.port` (both valid). Then inside `features`, `parse_bool` runs per boolean flag: `cache=True`
  (a `bool`, fine), then `debug=None`.
- **Value of the wrong type:** `debug=None` (JSON `null`) is a `NoneType`, neither `bool` nor `str`,
  so `parse_bool`'s string assumption does not hold.
- **State right before the crash:** the last call is `parse_bool(value=None)`; it crashes at
  `config_parser.py:150` executing `lowered = value.lower()` — `None` has no `.lower()` →
  `AttributeError`.

---

## 8. Program Slicing / Dependency Analysis

### Critical variable

`value`, the parameter of `parse_bool` (`config_parser.py:131`). At the crash it holds `None`, and
`value.lower()` (line 150) is the statement that raises the `AttributeError`.

### Input field affecting it

`features.debug` in the JSON config — set to `null` in `inputs/large_config_failure.json`. A JSON
`null` becomes Python `None` when parsed.

### Relevant functions

The backward slice (what determines `value`) runs through:

1. `load_config` (line 9) → `json.load(f)` (line 14): parses the file; `null` becomes `None` in
   `raw_config`.
2. `normalize_config` (line 19) → line 24: `normalize_features(config.get("features", {}))`.
3. `normalize_features` (line 68) → line 73: `debug = parse_bool(features.get("debug", False))` — passes
   `None` into `parse_bool`.
4. `parse_bool` (line 131): line 144 lets a `bool` through; line 150 runs `value.lower()` on `None`.

### Relevant lines

| Line | Statement | Role in the slice |
|---|---|---|
| 14 | `raw_config = json.load(f)` | JSON `null` becomes Python `None` |
| 24 | `features = normalize_features(config.get("features", {}))` | routes the features dict onward |
| 73 | `debug = parse_bool(features.get("debug", False))` | `None` reaches `parse_bool` (see note) |
| 144 | `if isinstance(value, bool):` | only `bool` is handled; `None` falls through |
| 150 | `lowered = value.lower()` | **crash** — assumes `value` is a string |

### Explanation

The assumption that breaks: `parse_bool` treats every non-`bool` value as string-like (it calls
`.lower()`), stated in its own comment (lines 147–149). `None` is neither `bool` nor `str`, so it slips
past line 144 and crashes at line 150.

Note on line 73: `features.get("debug", False)` does **not** guard against this. The default `False` is
returned only when the `debug` key is *absent*; here the key is *present* with value `null`, so `.get`
returns `None`, which is then handed to `parse_bool`.

---

## 9. Defect–Infection–Failure Chain

### Defect

The static flaw in the code: `parse_bool` (`config_parser.py:150`) calls `value.lower()` after only
special-casing `bool` (line 144). It assumes every non-`bool` value is string-like, with no handling
for `None` or other JSON types — stated in its own comment (lines 147–149). The defect is dormant until
a non-bool, non-string value reaches it.

### Infection

At runtime the defect is reached with `value = None` (from `features.debug: null`). The program enters
an erroneous state: control is at line 150, about to call `.lower()` on `None` — an operation invalid
for that type. (How `None` arrives here is the data slice of §8: `json.load` → `normalize_features`
line 73 → `parse_bool`.)

### Propagation

`None.lower()` raises `AttributeError`, which propagates **up the call stack uncaught**: `parse_bool` →
`normalize_features` (line 73) → `normalize_config` (line 24) → `load_config` (line 16) → `app.py`
`main`. `app.py` catches only `ConfigError`, so nothing intercepts an `AttributeError`.

### Failure

The externally observable result: the program terminates with an uncaught-exception traceback and exit
code **1** — a CRASH — instead of printing a clean `CONFIG_ERROR: ...` message. This is what the user
sees.

---

## 10. Patch

### Changed file/function

`src/config_parser.py` → `parse_bool` (the only changed file in the project).

### Explanation

The defect: `parse_bool` only special-cased `bool` and then called `value.lower()`, assuming every
remaining value was a string. JSON `null` (Python `None`), and likewise ints or lists, have no
`.lower()` and crashed with an uncaught `AttributeError`.

The fix is purely additive: a single guard before `value.lower()`. Any value that is not a `str` (and
not the already-handled `bool`) is rejected with a clean `ConfigError`, matching the function's own
documented contract — *"Any other value should raise ConfigError."* Nothing is removed or commented
out — `value.lower()` was never wrong, it only needed its input to be a string, which the guard now
guarantees.

This repairs the defect at its root (the wrong type assumption in `parse_bool`), not the symptom —
e.g. catching the exception in `app.py` would hide the crash while leaving the defect in place.

### Patch summary

```diff
     if isinstance(value, bool):
         return value

-    # Intentional defect:
-    # This assumes every non-bool value is string-like.
-    # Some valid JSON values, such as null, will break this assumption.
+    # A non-bool value must be a string to parse as a boolean; any other type
+    # (JSON null -> None, ints, lists, ...) is invalid, so raise ConfigError
+    # (matching this function's documented contract).
+    if not isinstance(value, str):
+        raise ConfigError(f"Invalid boolean value: {value}")
+
     lowered = value.lower()
```

---

## 11. Validation

Show that tests pass after your fix.

After the patch the full suite passes, the two valid configs are unchanged, and the previously crashing
input now produces a clean, controlled error instead of an uncaught traceback.

```bash
$ .venv/Scripts/python.exe -m pytest -q
...............                                                          [100%]
15 passed in 0.03s

$ py src/app.py inputs/valid_basic.json            # CONFIG_OK,  exit 0   (unchanged)
$ py src/app.py inputs/valid_full.json             # CONFIG_OK,  exit 0   (unchanged)
$ py src/app.py inputs/large_config_failure.json   # CONFIG_ERROR: Invalid boolean value: None,  exit 1
```

Before the fix the suite was 11 passed / 4 failed and `large_config_failure.json` crashed with an
uncaught `AttributeError`. After the fix all 15 tests pass — the 4 type tests (§4) now get the
`ConfigError` they expect — the valid configs still report `CONFIG_OK`, and the failing config exits
with a clean `CONFIG_ERROR` (no traceback). The full before-and-after `pytest` runs are captured in
`debugging_logs/test_results.md`.

---

## 12. Bonus: Regression Test

Optional.

---

## 13. Bonus: Mutation Testing

Optional.

| Mutant | Change | Killed? | Explanation |
|---|---|---|---|
| | | | |
