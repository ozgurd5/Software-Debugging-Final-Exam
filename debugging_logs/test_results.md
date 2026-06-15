# Test Results — Before and After the Fix (Question 9)

Full `pytest` runs showing the red → green transition for the Section 10 / Question 9 patch. Run from
the project root with `.venv\Scripts\python.exe -m pytest -q`. The two runs differ only in
`src/config_parser.py` (buggy vs patched `parse_bool`); the tests are identical. The suite has 16
tests: the Section 4 analysis suite plus the Bonus A regression test (`tests/test_regression.py`).

## Before the fix (buggy parser)

Five tests are red — the four type-handling tests (Section 4) and the Bonus A regression test all
expect a controlled `ConfigError`, but the unpatched `parse_bool` calls `.lower()` on a non-string and
crashes with `AttributeError`.

```text
......FFFF.....F                                                         [100%]
=========================== short test summary info ===========================
FAILED tests/test_config_cases.py::test_null_debug_raises_config_error
FAILED tests/test_config_cases.py::test_int_boolean_raises_config_error
FAILED tests/test_config_cases.py::test_list_boolean_raises_config_error
FAILED tests/test_config_cases.py::test_large_config_file_raises_config_error
FAILED tests/test_regression.py::test_regression_minimal_input_no_longer_fails
5 failed, 11 passed
```

## After the fix (patched parser)

`parse_bool` now rejects any non-string value with a clean `ConfigError`, so all five red tests turn
green and nothing else regresses.

```text
................                                                         [100%]
16 passed
```

The five tests that flip red → green are exactly the ones that pin the defect — the four type tests
plus the regression guard — so this is the evidence that the patch fixes the bug and breaks nothing
else.
