# JSON Config Parser Debugging Project

This is the starter project for the take-home final.

## Requirements

- Python 3.10+
- pytest

Install pytest if needed:

```bash
pip install pytest
```

## Run tests

```bash
pytest -q
```

## Run the application manually

```bash
python src/app.py inputs/valid_basic.json
python src/app.py inputs/valid_full.json
python src/app.py inputs/large_config_failure.json
```

The project contains a hidden defect. Your task is not only to fix it, but to systematically investigate it using debugging techniques.
