from src.config_parser import normalize_config, ConfigError

def is_failure(raw_config):
    try:
        normalize_config(raw_config)
    except ConfigError:
        return False   # controlled rejection -> expected
    except Exception:
        return True    # uncontrolled crash -> FAILURE
    return False       # normalized successfully -> expected
