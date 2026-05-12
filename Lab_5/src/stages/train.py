import os, sys
sys.path.append(os.getcwd())

from src.paths import get_dvc_config_path
from src.model_scripts.train import train
from src.stages.prepare_dataset import load_config


if __name__ == "__main__":
    cfg = load_config(get_dvc_config_path())
    train(cfg)
