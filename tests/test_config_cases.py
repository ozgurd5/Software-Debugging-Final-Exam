from pathlib import Path
import pytest

from src.config_parser import load_config, normalize_config, ConfigError
from oracle import is_failure


BASE = Path(__file__).resolve().parents[1]
INPUTS = BASE / "inputs"


def test_valid_minimal_defaults():
    raw = {
        "server": {},
        "features": {},
        "limits": {},
    }

    config = normalize_config(raw)

    assert config["server"]["host"] == "localhost"
    assert config["server"]["port"] == 8080
    assert config["features"]["cache"] is False
    assert config["limits"]["max_users"] == 100
    assert config["logging"]["level"] == "INFO"


def test_alternative_string_booleans():
    raw = {
        "server": {},
        "features": {"cache": "1", "debug": "0", "experimental": "yes"},
        "limits": {},
    }

    config = normalize_config(raw)

    assert config["features"]["cache"] is True
    assert config["features"]["debug"] is False
    assert config["features"]["experimental"] is True


def test_real_booleans_passthrough():
    raw = {
        "server": {},
        "features": {"cache": True, "debug": False},
        "limits": {},
    }

    config = normalize_config(raw)

    assert config["features"]["cache"] is True
    assert config["features"]["debug"] is False


def test_oracle_marks_valid_config_as_expected():
    raw = {
        "server": {"host": "localhost", "port": 8080},
        "features": {"cache": True, "debug": False},
        "limits": {"max_users": 50, "timeout": 10},
    }

    assert is_failure(raw) is False


def test_invalid_logging_level_raises_config_error():
    raw = {
        "server": {},
        "features": {},
        "limits": {},
        "logging": {"level": "VERBOSE"},
    }

    with pytest.raises(ConfigError):
        normalize_config(raw)


def test_non_object_section_raises_config_error():
    raw = {
        "server": "localhost",
        "features": {},
        "limits": {},
    }

    with pytest.raises(ConfigError):
        normalize_config(raw)


def test_null_debug_raises_config_error():
    raw = {
        "server": {},
        "features": {"debug": None},
        "limits": {},
    }

    with pytest.raises(ConfigError):
        normalize_config(raw)


def test_int_boolean_raises_config_error():
    raw = {
        "server": {},
        "features": {"cache": 1},
        "limits": {},
    }

    with pytest.raises(ConfigError):
        normalize_config(raw)


def test_list_boolean_raises_config_error():
    raw = {
        "server": {},
        "features": {"experimental": []},
        "limits": {},
    }

    with pytest.raises(ConfigError):
        normalize_config(raw)


def test_large_config_file_raises_config_error():
    with pytest.raises(ConfigError):
        load_config(INPUTS / "large_config_failure.json")
