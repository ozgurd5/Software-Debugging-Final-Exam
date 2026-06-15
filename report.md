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

Each hypothesis was tested with a **controlled experiment**: start from the real failing input
`inputs/large_config_failure.json` and change exactly one thing, observing the outcome (normalizes
OK / clean `ConfigError` / uncontrolled crash). The experiments are runnable in
`debugging_logs/hypothesis_experiments.py`; their captured output is in
`debugging_logs/hypothesis_experiments_output.md`.

| Hypothesis | Observation | Experiment | Result | Accepted/Rejected |
|---|---|---|---|---|
| **H1** — A JSON `null` (Python `None`) in a boolean field is what triggers the failure. | In `large_config_failure.json`, `features.debug` is `null`, and the traceback shows the crash happens exactly while that field is parsed, inside `parse_bool`. | Run the real file as-is (`debug: null`), then change **only** `features.debug` to `false` (control). | As-is → crash (`AttributeError`); with `false` → normalizes fine. Only `debug` changed, so the `null` value is the trigger. | **Accepted** |
| **H2** — The cause is not specific to `null`: **any** non-bool, non-string value (int, list, float) crashes the same way, because `parse_bool` assumes a string. | Right after its `isinstance(value, bool)` check, `parse_bool` calls `value.lower()`, which only strings support. | On the real file, set `features.debug` to `1` (int), then `[]` (list), then `1.5` (float). | All three crash with `AttributeError: '<type>' object has no attribute 'lower'`. The cause generalises to any non-bool, non-string value. | **Accepted** |
| **H3** — The failure is caused by a **missing** required section (rather than a bad value). | The file has several sections, so a missing one is a plausible alternative cause. | Remove the `limits` section from the real file and run. | A clean `ConfigError: Missing required section: limits` — a *controlled* rejection, not a crash. A missing section is handled correctly, so it is not the cause. | **Rejected** |
| **H4** — The failure is caused by the large / deeply-nested structure (`services`, `security`, `metadata`, ...). | The failing file is big and nested, unlike the small valid files, so the structure is a plausible alternative cause. | From the real file: (a) remove the nested sections but keep `debug=null`; (b) keep the nested sections but set `debug=false`. | (a) still crashes; (b) normalizes fine. The parser ignores those nested sections entirely, so nesting changes nothing — only the `null` value matters. | **Rejected** |

Conclusion: the crash is caused by `parse_bool` calling `.lower()` on a non-string value — narrowed by
H1 (the `null` in `features.debug`) and generalised by H2 (any non-bool, non-string value). It is
**independent** of missing sections (H3) and of the large/nested structure (H4).

---

## 6. Delta Debugging / Input Minimization

### Original input size

`inputs/large_config_failure.json`: ≈61 lines, 7 top-level sections (`metadata`, `server`,
`features`, `limits`, `logging`, `services`, `security`); `features` alone has 5 keys.

### Reduction steps

A **systematic greedy minimizer** (`debugging_logs/delta_debugging.py`) automatically visits every
element (each key, at any depth) and deletes it only if the crash still occurs (decided by
`tests/oracle.is_failure`), repeating until nothing more can be removed. Full trace:
`debugging_logs/delta_debugging_output.md`. **Phase 1** — each deletion, one element per step:

| Step | Change attempted | Failure remained? | Conclusion |
|---|---|---|---|
| 1 | remove `metadata` | Yes | irrelevant → removed |
| 2 | remove `server.host` | Yes | irrelevant → removed |
| 3 | remove `server.port` | Yes | `server` now `{}` → removed |
| 4 | remove `features.cache` | Yes | not the trigger → removed |
| 5 | remove `features.experimental` | Yes | not the trigger → removed |
| 6 | remove `features.recommendations` | Yes | unused key → removed |
| 7 | remove `features.new_checkout` | Yes | unused key → removed |
| 8 | remove `limits.max_users` | Yes | irrelevant → removed |
| 9 | remove `limits.timeout` | Yes | irrelevant → removed |
| 10 | remove `limits.retries` | Yes | `limits` now `{}` → removed |
| 11 | remove `logging` | Yes | irrelevant → removed |
| 12 | remove `services` | Yes | irrelevant → removed |
| 13 | remove `security` | Yes | irrelevant → removed |

**Phase 2 — 1-minimality check.** A failure-inducing input is **1-minimal** when removing *any* single
remaining element makes the failure disappear (so it cannot be shrunk any further). Each remaining
element was deleted in turn:

| Change attempted | Failure remained? | Conclusion |
|---|---|---|
| remove `server` | No (clean `ConfigError`) | required section → kept |
| remove `features` | No (clean `ConfigError`) | required section → kept |
| remove `features.debug` | No (normalizes OK) | **the trigger** (the `null`) → kept |
| remove `limits` | No (clean `ConfigError`) | required section → kept |

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
`validate_required_sections` raises a clean `ConfigError` (Phase 2) — a different outcome, not the
crash. With all three present, `normalize_features` calls `parse_bool(features["debug"])` =
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

- **Sections processed:** `server` is normalized successfully, then `features` begins. `limits` and
  `logging` are never reached — the program crashes inside `features`.
- **Fields normalized:** inside `features`, `parse_bool` runs per boolean flag: `cache=True` (a `bool`,
  fine), then `debug=None`.
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
with a clean `CONFIG_ERROR` (no traceback).

---

## 12. Bonus: Regression Test

Optional.

---

## 13. Bonus: Mutation Testing

Optional.

| Mutant | Change | Killed? | Explanation |
|---|---|---|---|
| | | | |
