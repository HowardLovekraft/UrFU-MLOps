from typing import Any
import yaml


def load_config(config_path):
    with open(config_path) as conf_file:
        config: dict[str, Any] = yaml.safe_load(conf_file)
    return config
