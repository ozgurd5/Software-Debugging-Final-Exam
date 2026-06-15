# Delta Debugging — Minimization Output (Question 5)

Produced by running `py debugging_logs/delta_debugging.py` from the project root. The script is a
systematic greedy minimizer: **Phase 1** deletes every element it can while the crash remains;
**Phase 2** checks the result is *1-minimal* (removing any single remaining element makes the failure
disappear). Pass/fail is decided by the Question 2 oracle.

```text
original -> failure

Phase 1 -- greedy reduction (one element per step):
  step  1: remove metadata                   -> failure remains  (KEEP)
  step  2: remove server.host                -> failure remains  (KEEP)
  step  3: remove server.port                -> failure remains  (KEEP)
  step  4: remove features.cache             -> failure remains  (KEEP)
  step  5: remove features.experimental      -> failure remains  (KEEP)
  step  6: remove features.recommendations   -> failure remains  (KEEP)
  step  7: remove features.new_checkout      -> failure remains  (KEEP)
  step  8: remove limits.max_users           -> failure remains  (KEEP)
  step  9: remove limits.timeout             -> failure remains  (KEEP)
  step 10: remove limits.retries             -> failure remains  (KEEP)
  step 11: remove logging                    -> failure remains  (KEEP)
  step 12: remove services                   -> failure remains  (KEEP)
  step 13: remove security                   -> failure remains  (KEEP)

minimal failure-inducing input:
{
  "server": {},
  "features": {
    "debug": null
  },
  "limits": {}
}

Phase 2 -- 1-minimality check (each remaining element is essential):
  remove server           -> no failure  -> essential, kept
  remove features         -> no failure  -> essential, kept
  remove features.debug   -> no failure  -> essential, kept
  remove limits           -> no failure  -> essential, kept
```

Phase 1 removed 13 elements; all are irrelevant to the crash. Phase 2 shows the four remaining
elements are each essential: removing a required section (`server` / `features` / `limits`) yields a
clean `ConfigError`, and removing `features.debug` leaves no `null` so the program normalizes — both
are *different outcomes*, not the crash. Minimal failure-inducing input:
`{"server": {}, "features": {"debug": null}, "limits": {}}`.
