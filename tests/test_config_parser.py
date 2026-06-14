from pathlib import Path
import pytest

from src.config_parser import load_config, normalize_config, ConfigError


BASE = Path(__file__).resolve().parents[1]
INPUTS = BASE / "inputs"


def test_valid_basic_config_loads():
    config = load_config(INPUTS / "valid_basic.json")
    assert config["server"]["host"] == "localhost"
    assert config["server"]["port"] == 8080


def test_string_boolean_values_are_supported():
    raw = {
        "server": {"host": "localhost", "port": 8080},
        "features": {"cache": "true", "debug": "false"},
        "limits": {"max_users": 50, "timeout": 10},
    }

    config = normalize_config(raw)

    assert config["features"]["cache"] is True
    assert config["features"]["debug"] is False


def test_invalid_port_raises_config_error():
    raw = {
        "server": {"host": "localhost", "port": 70000},
        "features": {"cache": True, "debug": False},
        "limits": {"max_users": 50, "timeout": 10},
    }

    with pytest.raises(ConfigError):
        normalize_config(raw)


def test_missing_required_section_raises_config_error():
    raw = {
        "server": {"host": "localhost", "port": 8080},
        "features": {"cache": True, "debug": False},
    }

    with pytest.raises(ConfigError):
        normalize_config(raw)


def test_valid_full_config_loads():
    config = load_config(INPUTS / "valid_full.json")
    assert config["features"]["cache"] is True
    assert config["features"]["debug"] is False
    assert config["logging"]["level"] == "WARNING"
