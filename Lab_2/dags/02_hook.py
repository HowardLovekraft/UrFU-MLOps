from datetime import datetime
import json
import logging
import os

from airflow.sdk import DAG
from airflow.providers.standard.operators.python import PythonOperator
from hooks import CarsHook  # ← импортируем из plugins/hooks/
import pandas as pd
from sklearn.preprocessing import OrdinalEncoder


# Настройка логгера
logger = logging.getLogger(__name__)


def _fetch_cars(conn_id: str, templates_dict: dict, batch_size: int = 1000, **_):
    logger = logging.getLogger(__name__)
    output_path = templates_dict["output_path"]

    logger.info("Fetching all cars from the API...")
    hook = CarsHook(conn_id=conn_id)
    cars = list(hook.get_cars(batch_size=batch_size))
    logger.info(f"Fetched {len(cars)} car records")

    # Убедимся, что директория существует
    output_dir = os.path.dirname(output_path)
    os.makedirs(output_dir, exist_ok=True)

    with open(output_path, "w") as f:
        json.dump(cars, f)

    logger.info(f"Saved cars to {output_path}")


def clean_cars(**context):
    data_path = "/data/cars/cars_full.json"
    df = pd.read_json(data_path)

    cat_columns = ['Make', 'Model', 'Style', 'Fuel_type', 'Transmission']
    num_columns = ['Year', 'Distance', 'Engine_capacitycm3', 'Priceeuro']
     
    # Удаление строк с пропусками
    df = df.dropna()
    
    # Удаление дубликатов
    df = df.drop_duplicates()
    
    # Преобразование категориальных признаков
    df = df.reset_index(drop=True)
    ordinal = OrdinalEncoder()
    ordinal.fit(df[cat_columns])
    Ordinal_encoded = ordinal.transform(df[cat_columns])
    df_ordinal = pd.DataFrame(Ordinal_encoded, columns=cat_columns)
    df[cat_columns] = df_ordinal[cat_columns]
    os.makedirs('/data/cleaned', exist_ok=True)
    df.to_json("/data/cleaned/cars_cleaned.json")


with DAG(
    dag_id="02_hook",
    description="Fetches car data from the custom API using a custom hook.",
    start_date=datetime(2026, 2, 3),
    schedule="@daily",
    catchup=False,
    max_active_runs=1,
) as dag:

    fetch_task = PythonOperator(
        task_id="fetch_cars",
        python_callable=_fetch_cars,
        op_kwargs={"conn_id": "carsapi"},  # ← имя Airflow Connection
        templates_dict={
            "output_path": "/data/custom_hook/cars.json",
        },
    )
    clean_task = PythonOperator(
        task_id="clean_cars_data",
        python_callable=clean_cars,

    )
    
    fetch_task >> clean_task
