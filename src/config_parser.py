import json
from pathlib import Path


class ConfigError(Exception):
    """Raised when the configuration file is invalid."""


def load_config(path):
    """Load and validate a JSON configuration file."""
    path = Path(path)

    with path.open("r", encoding="utf-8") as f:
        raw_config = json.load(f)

    return normalize_config(raw_config)


def normalize_config(config):
    """Normalize raw JSON config into an application config dictionary."""
    validate_required_sections(config)

    server = normalize_server(config.get("server", {}))
    features = normalize_features(config.get("features", {}))
    limits = normalize_limits(config.get("limits", {}))
    logging_config = normalize_logging(config.get("logging", {}))

    return {
        "server": server,
        "features": features,
        "limits": limits,
        "logging": logging_config,
    }


def validate_required_sections(config):
    if not isinstance(config, dict):
        raise ConfigError("Top-level configuration must be a JSON object")

    required = ["server", "features", "limits"]
    for section in required:
        if section not in config:
            raise ConfigError(f"Missing required section: {section}")


def normalize_server(server):
    if not isinstance(server, dict):
        raise ConfigError("server section must be an object")

    host = server.get("host", "localhost")
    port = server.get("port", 8080)

    if not isinstance(host, str) or not host:
        raise ConfigError("server.host must be a non-empty string")

    if not isinstance(port, int):
        raise ConfigError("server.port must be an integer")

    if port <= 0 or port > 65535:
        raise ConfigError("server.port must be between 1 and 65535")

    return {
        "host": host,
        "port": port,
    }


def normalize_features(features):
    if not isinstance(features, dict):
        raise ConfigError("features section must be an object")

    cache = parse_bool(features.get("cache", False))
    debug = parse_bool(features.get("debug", False))
    experimental = parse_bool(features.get("experimental", False))

    return {
        "cache": cache,
        "debug": debug,
        "experimental": experimental,
    }


def normalize_limits(limits):
    if not isinstance(limits, dict):
        raise ConfigError("limits section must be an object")

    max_users = limits.get("max_users", 100)
    timeout = limits.get("timeout", 30)
    retries = limits.get("retries", 3)

    if not isinstance(max_users, int) or max_users <= 0:
        raise ConfigError("limits.max_users must be a positive integer")

    if not isinstance(timeout, int) or timeout <= 0:
        raise ConfigError("limits.timeout must be a positive integer")

    if not isinstance(retries, int) or retries < 0:
        raise ConfigError("limits.retries must be a non-negative integer")

    return {
        "max_users": max_users,
        "timeout": timeout,
        "retries": retries,
    }


def normalize_logging(logging_config):
    if not isinstance(logging_config, dict):
        raise ConfigError("logging section must be an object")

    level = logging_config.get("level", "INFO")
    destination = logging_config.get("destination", "stdout")

    if not isinstance(level, str):
        raise ConfigError("logging.level must be a string")

    level = level.upper()

    if level not in ["DEBUG", "INFO", "WARNING", "ERROR"]:
        raise ConfigError("Invalid logging.level")

    if destination not in ["stdout", "stderr", "file"]:
        raise ConfigError("Invalid logging.destination")

    return {
        "level": level,
        "destination": destination,
    }


def parse_bool(value):
    """
    Parse boolean-like configuration values.

    Accepted values:
    - True / False
    - "true" / "false"
    - "yes" / "no"
    - "1" / "0"

    Any other value should raise ConfigError.
    """

    if isinstance(value, bool):
        return value

    # A non-bool value must be a string to parse as a boolean; any other type
    # (JSON null -> None, ints, lists, ...) is invalid, so raise ConfigError
    # (matching this function's documented contract).
    if not isinstance(value, str):
        raise ConfigError(f"Invalid boolean value: {value}")

    lowered = value.lower()

    if lowered in ["true", "yes", "1"]:
        return True

    if lowered in ["false", "no", "0"]:
        return False

    raise ConfigError(f"Invalid boolean value: {value}")
