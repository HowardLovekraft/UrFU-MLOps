from pathlib import Path


import kagglehub
from kagglehub import KaggleDatasetAdapter
from loguru import logger
import numpy as np
import pandas as pd
from sklearn.preprocessing import OrdinalEncoder

import os, sys
sys.path.append(os.getcwd())

from src.paths import get_dataset_path, get_dvc_config_path
from src.utils import load_config


def download_data(dataset_path: Path = get_dataset_path()) -> None:
    """
    Скачивает датасет с продажами шоколада из Kagglehub.

    :param dataset_path: Путь, где будет сохранен датасет.
    """
    if not dataset_path.exists():
        df = kagglehub.dataset_load(
            KaggleDatasetAdapter.PANDAS,
            "saidaminsaidaxmadov/chocolate-sales",
            "Chocolate Sales (2).csv"
        )
        df.to_csv(dataset_path, index=False)
        print("df: ", df.shape)
    else:
        print("Load predownloaded dataset")


def clear_data(path2data: Path = get_dataset_path()) -> pd.DataFrame:
    def ordinal_encode(orig_df: pd.DataFrame, cols: list[str]) -> pd.DataFrame:
        df = orig_df.copy()
        df = df.reset_index(drop=True)
        ordinal = OrdinalEncoder(handle_unknown='use_encoded_value', unknown_value=1337)
        ordinal.fit(df[cat_columns])
        ordinal_encoded = ordinal.transform(df[cat_columns])
        df_ordinal = pd.DataFrame(ordinal_encoded, columns=cat_columns)
        df[cat_columns] = df_ordinal[cat_columns]
        return df


    df = pd.read_csv(
        str(path2data), date_format="%d/%m/%Y", parse_dates=["Date"]
    )

    cat_columns = ["Sales Person", "Country", "Product"]
    num_columns = ["Amount", "Boxes Shipped", "Date"]

    # Анализ и очистка данных
    df["Amount"] = df["Amount"].str.replace("$", "")
    df["Amount"] = df["Amount"].str.replace(",", "")
    df["Amount"] = df["Amount"].astype(np.float32)
    df["Date"] = df["Date"].astype('int64') // 10**9

    # Категоризация данных
    df = ordinal_encode(df, cat_columns)
    return df


def featurize(df: pd.DataFrame, config: dict) -> None:
    logger.info("Create features")
    df['amount_per_box'] = df.Amount / df['Boxes Shipped']

    features_path = config['featurize']['features_path']
    df.to_csv(features_path, index=False)


if __name__ == '__main__':
    cfg = load_config(get_dvc_config_path())
    download_data()
    df_prep = clear_data(cfg['data_load']['dataset_csv'])
    df_new_features = featurize(df_prep, cfg)
