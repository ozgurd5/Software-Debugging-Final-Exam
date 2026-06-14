import sys
from config_parser import load_config, ConfigError


def main():
    if len(sys.argv) != 2:
        print("Usage: python src/app.py <config_file>")
        return 2

    path = sys.argv[1]

    try:
        config = load_config(path)
        print("CONFIG_OK")
        print(config)
        return 0
    except ConfigError as e:
        print(f"CONFIG_ERROR: {e}")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
