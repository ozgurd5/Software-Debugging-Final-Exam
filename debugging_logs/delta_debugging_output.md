# Delta Debugging — Minimization Output (Question 5)

Produced by running `py debugging_logs/delta_debugging.py` from the project root, on the **original
(buggy) parser** (the crash is present). One annotated greedy pass tries to delete every element: keep
the deletion if the crash survives (REMOVED — the element is irrelevant), otherwise leave it in place
(ESSENTIAL — removing it changes the outcome). The crash / no-crash decision is the Question 2 oracle.

```text
original -> failure

Greedy pass -- delete each element; keep the deletion only if the crash survives:
  delete metadata                  -> still crashes     -> REMOVED
  delete server                    -> clean ConfigError -> ESSENTIAL
  delete server.host               -> still crashes     -> REMOVED
  delete server.port               -> still crashes     -> REMOVED
  delete features                  -> clean ConfigError -> ESSENTIAL
  delete features.cache            -> still crashes     -> REMOVED
  delete features.debug            -> normalizes OK     -> ESSENTIAL
  delete features.experimental     -> still crashes     -> REMOVED
  delete features.recommendations  -> still crashes     -> REMOVED
  delete features.new_checkout     -> still crashes     -> REMOVED
  delete limits                    -> clean ConfigError -> ESSENTIAL
  delete limits.max_users          -> still crashes     -> REMOVED
  delete limits.timeout            -> still crashes     -> REMOVED
  delete limits.retries            -> still crashes     -> REMOVED
  delete logging                   -> still crashes     -> REMOVED
  delete services                  -> still crashes     -> REMOVED
  delete security                  -> still crashes     -> REMOVED

minimal failure-inducing input:
{
  "server": {},
  "features": {
    "debug": null
  },
  "limits": {}
}
```

13 elements are REMOVED (irrelevant to the crash); 4 are ESSENTIAL — the required sections `server`,
`features`, `limits` (deleting any one yields a clean `ConfigError`, a different outcome) and
`features.debug` (deleting the `null` lets the program normalize). The ESSENTIAL rows are the
irreducible core: the minimal failure-inducing input is
`{"server": {}, "features": {"debug": null}, "limits": {}}`.
