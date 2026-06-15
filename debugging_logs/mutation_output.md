# Mutation Testing — Output (Bonus B)

Produced by running `.venv\Scripts\python.exe debugging_logs/mutation_test.py` from the project root,
against the **patched** parser. The script applies each mutation to `src/config_parser.py` one at a
time, runs the full 16-test suite, records KILLED (a test fails) or SURVIVED (all tests pass — a gap),
then restores the source. The baseline (no mutation) is green, so the measurement is valid.

```text
baseline (no mutation) -> all tests pass

Mutants (KILLED = suite caught it; SURVIVED = gap in the tests):
  M1  KILLED    parse_bool: drop the non-string guard (reverts the fix)
  M2  KILLED    parse_bool: drop "1" from the accepted true values
  M3  KILLED    normalize_logging: also accept "VERBOSE" as a valid level
  M4  KILLED    validate_required_sections: invert the presence check (not in -> in)
  M5  SURVIVED  normalize_server: weaken the port upper bound (> -> >=)
  M6  KILLED    normalize_features: change the cache default (False -> True)

mutation score: 5/6 killed
```

5 of 6 mutants are killed (mutation score 5/6 ≈ 83%). The survivor **M5** changes behaviour only for
`port == 65535` (now rejected); no test exercises that exact upper boundary, so it slips through — a
real gap the suite could close with a `server.port = 65535` test that expects success.
