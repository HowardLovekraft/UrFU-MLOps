from datetime import datetime
import json
import logging
import os
import requests

from airflow import DAG
from airflow.providers.standard.operators.python import PythonOperator
import pandas as pd
from sklearn.preprocessing import OrdinalEncoder

# Параметры подключения к вашему API
MOVIELENS_HOST = os.environ.get("MOVIELENS_HOST", "carsapi")
MOVIELENS_SCHEMA = os.environ.get("MOVIELENS_SCHEMA", "http")
MOVIELENS_PORT = os.environ.get("MOVIELENS_PORT", "8081")

MOVIELENS_USER = os.environ["MOVIELENS_USER"]
MOVIELENS_PASSWORD = os.environ["MOVIELENS_PASSWORD"]

# Настройка логгера
logger = logging.getLogger(__name__)


def _get_session():
    """Создаёт сессию для запросов к вашему Car API."""
    session = requests.Session()
    session.auth = (MOVIELENS_USER, MOVIELENS_PASSWORD)
    base_url = f"{MOVIELENS_SCHEMA}://{MOVIELENS_HOST}:{MOVIELENS_PORT}"
    return session, base_url


def _get_all_cars(batch_size=100):
    """Получает все записи из /cars с пагинацией."""
    session, base_url = _get_session()
    url = f"{base_url}/cars"

    offset = 0
    total = None
    all_cars = []

    while total is None or offset < total:
        params = {"offset": offset, "limit": batch_size}
        response = session.get(url, params=params)
        response.raise_for_status()
        data = response.json()

        all_cars.extend(data["result"])
        offset += batch_size
        total = data["total"]

        if len(data["result"]) == 0:
            break

    return all_cars


def fetch_cars(**context):
    """Загружает все автомобили и сохраняет в JSON."""
    logger.info("Fetching all cars from the API...")

    cars = _get_all_cars(batch_size=100)
    logger.info(f"Fetched {len(cars)} car records.")

    # Путь для сохранения
    output_path = "/data/cars/cars_full.json"
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    with open(output_path, "w") as f:
        json.dump(cars, f)

    logger.info(f"Saved cars to {output_path}")


def analyze_cars(**context):
    """Анализирует данные: например, средняя цена по году."""
    input_path = "/data/cars/cars_full.json"
    output_path = "/data/cars/price_by_year.csv"

    logger.info(f"Reading cars from {input_path}")
    df = pd.read_json(input_path)

    if df.empty:
        logger.warning("No car data to analyze.")
        return

    # Пример анализа: средняя цена по году
    summary = df.groupby("Year")["Priceeuro"].agg(
        mean_price="mean",
        count="count",
        min_price="min",
        max_price="max"
    ).round(2)

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    summary.to_csv(output_path)
    logger.info(f"Analysis saved to {output_path}")


def clean_cars(**context):
    data_path = "/data/cars/cars_full.json"
    df = pd.read_json(data_path)

    cat_columns = ['Make', 'Model', 'Style', 'Fuel_type', 'Transmission']
    num_columns = ['Year', 'Distance', 'Engine_capacity(cm3)', 'Price(euro)']

    question_dist = df[(df.Year < 2021) & (df.Distance < 1100)]
    df = df.drop(question_dist.index)

    # Анализ и очистка данных
    question_dist = df[(df.Distance > 1e6)]
    df = df.drop(question_dist.index)

    question_engine = df[
        (df["Engine_capacitycm3"] < 200) & (df["Engine_capacitycm3"] > 5000)
    ]
    df = df.drop(question_engine.index)

    question_price = df[
        (df["Priceeuro"] < 101) & (df["Priceeuro"] > 1e5)
    ]
    df = df.drop(question_price.index)

    question_year = df[df.Year < 1971]
    df = df.drop(question_year.index)

    df = df.reset_index(drop=True)
    ordinal = OrdinalEncoder()
    ordinal.fit(df[cat_columns])
    Ordinal_encoded = ordinal.transform(df[cat_columns])
    df_ordinal = pd.DataFrame(Ordinal_encoded, columns=cat_columns)
    df[cat_columns] = df_ordinal[cat_columns]
    os.makedirs('/data/cleaned', exist_ok=True)
    df.to_json("/data/cleaned/cars_cleaned.json")


# Определяем DAG
with DAG(
    dag_id="01_cars",
    description="Fetches car data from the custom API and analyzes it.",
    start_date=datetime(2026, 2, 3),  # сегодняшняя дата (ваш контекст)
    schedule="@daily",               # можно оставить daily или сделать @once
    catchup=False,
    max_active_runs=1,
) as dag:

    fetch_task = PythonOperator(
        task_id="fetch_cars",
        python_callable=fetch_cars,
    )

    analyze_task = PythonOperator(
        task_id="analyze_cars",
        python_callable=analyze_cars,
    )
    clean_task = PythonOperator(
        task_id="clean_cars_data",
        python_callable=clean_cars,

    )

    fetch_task >> analyze_task >> clean_task
