# Trace / Logging — Output (Question 6)

Produced by running `py debugging_logs/trace_run.py` from the project root. The script wraps the
parser's functions at runtime (the instructor's source is untouched) and logs each section/field as it
is processed, then reports the state at the crash.

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

Reading: `server` normalizes successfully, then `features` begins. `parse_bool` succeeds on
`cache=True` (a `bool`) but is then called with `debug=None` (a `NoneType` — neither `bool` nor
`str`) and crashes one line later at `config_parser.py:150` (`value.lower()` on `None`). `limits` and
`logging` are never reached, because the crash happens inside `features`.
