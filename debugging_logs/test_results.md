# Test Results — Before and After the Fix (Question 9)

Full `pytest` runs showing the red → green transition for the Section 10 / Question 9 patch. Run from
the project root with `.venv\Scripts\python.exe -m pytest -q`. The two runs differ only in
`src/config_parser.py` (buggy vs patched `parse_bool`); the tests are identical.

## Before the fix (buggy parser)

The four type-handling tests assert a clean `ConfigError`, but the unpatched `parse_bool` calls
`.lower()` on a non-string value and crashes with `AttributeError`, so they are red.

```text
......FFFF.....                                                          [100%]
=========================== short test summary info ===========================
FAILED tests/test_config_cases.py::test_null_debug_raises_config_error
FAILED tests/test_config_cases.py::test_int_boolean_raises_config_error
FAILED tests/test_config_cases.py::test_list_boolean_raises_config_error
FAILED tests/test_config_cases.py::test_large_config_file_raises_config_error
4 failed, 11 passed
```

## After the fix (patched parser)

`parse_bool` now rejects any non-string value with a clean `ConfigError`, so the four tests receive the
`ConfigError` they expect and turn green. No previously passing test regresses.

```text
...............                                                          [100%]
15 passed
```

The four tests that flip red → green are exactly the ones that pin the defect: this is the evidence
that the patch fixes the bug and breaks nothing else.
