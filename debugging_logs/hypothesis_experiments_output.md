# Scientific Debugging — Experiment Output (Question 4)

Produced by running `py debugging_logs/hypothesis_experiments.py` from the project root. Every
experiment starts from the real `inputs/large_config_failure.json` and changes exactly one thing in
memory (the bundled file itself is never modified).

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

Legend: `CRASH` = uncontrolled crash (the bug); `ConfigError (controlled)` = clean, designed
rejection; `OK` = normalized successfully.

Reading the results (full hypothesis table: report.md §5 / exam_answers.md S4):
- **H1 — Accepted.** `debug=null` crashes; the single change `debug=false` normalizes, so the `null` value is the trigger.
- **H2 — Accepted.** int, list and float all crash the same way, so any non-bool, non-string value triggers it (root cause: `parse_bool` assumes a string).
- **H3 — Rejected.** Removing the `limits` section yields a controlled `ConfigError`, not a crash; a missing section is handled correctly.
- **H4 — Rejected.** Removing the nested sections still crashes (the `null` is still there); keeping them with `debug=false` is fine — nesting is irrelevant, the value decides.
