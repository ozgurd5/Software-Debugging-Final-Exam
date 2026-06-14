# Debugging Report

## 1. Project and Environment

- Student name:
- Student number:
- Python version:
- Operating system:
- Date:

---

## 2. Failure Reproduction

### Command

```bash

```

### Observed failure

```text

```

### Failure type

Crash / wrong output / unexpected behavior:

---

## 3. Test Oracle

Explain how your oracle decides whether the program passed or failed.

```python

```

---

## 4. Passing and Failing Tests

| Test name | Input summary | Expected result | Actual result | Pass/Fail |
|---|---|---|---|---|
| | | | | |

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
