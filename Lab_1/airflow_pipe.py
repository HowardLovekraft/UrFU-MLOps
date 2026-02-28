from datetime import datetime, timedelta
import os
from pathlib import Path
import requests
 
from airflow import DAG
from airflow.providers.standard.operators.python import PythonOperator
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
 
dag_sales = DAG(
    dag_id="tasty_chocolate_pipe",
    start_date=datetime(2026, 2, 28),
    schedule=timedelta(minutes=5),
    max_active_runs=1,
    catchup=False,
)
download_task = PythonOperator(python_callable=download_data, task_id = "download_chocolate_sales", dag = dag_sales)
clear_task = PythonOperator(python_callable=clear_data, task_id = "clear_chocolate_sales", dag = dag_sales)
train_task = PythonOperator(python_callable=train, task_id = "train_chocolate_sales", dag = dag_sales)
download_task >> clear_task >> train_task
