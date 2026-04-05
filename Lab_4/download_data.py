from datetime import datetime, timedelta
import os
from pathlib import Path
import requests
 
import kagglehub
from kagglehub import KaggleDatasetAdapter
import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler, OrdinalEncoder, OneHotEncoder, PowerTransformer
from sklearn.compose import ColumnTransformer # т.н. преобразователь колонок
 
from train_model import train
 
def download_data():
    df = kagglehub.load_dataset(
        KaggleDatasetAdapter.PANDAS,
        "saidaminsaidaxmadov/chocolate-sales",
        "Chocolate Sales (2).csv"
    )
    df.to_csv("chocolate_sales.csv", index = False)
    print("df: ", df.shape)
    return df
 
def clear_data():
    df = pd.read_csv("chocolate_sales.csv", date_format="%d/%m/%Y", parse_dates=["Date"])
 
    cat_columns = ["Sales Person", "Country", "Product"]
    num_columns = ["Amount", "Boxes Shipped", "Date"]
 
    # Анализ и очистка данных
    df["Amount"] = df["Amount"].str.replace("$", "")
    df["Amount"] = df["Amount"].str.replace(",", "")
    df["Amount"] = df["Amount"].astype(np.float32)
 
    df["Date"] = df["Date"].astype('int64') // 10**9
 
    df = df.reset_index(drop=True)  
    ordinal = OrdinalEncoder()
    ordinal.fit(df[cat_columns]);
    Ordinal_encoded = ordinal.transform(df[cat_columns])
    df_ordinal = pd.DataFrame(Ordinal_encoded, columns=cat_columns)
    df[cat_columns] = df_ordinal[cat_columns]
    df.to_csv('df_clear.csv')
    return True
 

download_data()
clear_data()
