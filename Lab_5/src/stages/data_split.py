from typing import Any


from loguru import logger
import pandas as pd
from sklearn.model_selection import train_test_split



import os, sys
sys.path.append(os.getcwd())

from src.utils import load_config
from src.paths import get_dvc_config_path


def data_split(cfg: dict[str, Any]):
    df = pd.read_csv(cfg['featurize']['features_path'])
    train, test = train_test_split(
        df,
        test_size=cfg['data_split']['test_size'],
        random_state=42
    )
    logger.info('Save train and test sets')

    train_path = cfg['data_split']['trainset_path']
    test_path = cfg['data_split']['testset_path']
    train.to_csv(train_path, index=False)
    test.to_csv(test_path, index=False)


if __name__ =='__main__':
    cfg = load_config(get_dvc_config_path())
    data_split(cfg)
