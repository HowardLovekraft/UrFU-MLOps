from pathlib import Path
from typing import Final, Callable


def fixdir(func: Callable[[], Path]):
    """Создает директорию, если её не существует."""
    def wrapper() -> Path:
        dir_path = func()
        if dir_path:
            dir_path.mkdir(parents=True, exist_ok=True)
        return dir_path
    return wrapper


def get_dvc_config_path() -> Path:
    """Возвращает путь до конфига DVC."""
    return get_sources_dpath() / 'config.yaml'


def get_dataset_path() -> Path:
    """Возвращает путь к датасету с продажами шоколада."""
    return get_data_dpath() / 'chocolate_sales.csv'


@fixdir
def get_data_dpath() -> Path:
    """Возвращает путь к директории с датасетами."""
    return get_project_root() / 'data'


@fixdir
def get_sources_dpath() -> Path:
    """Возвращает путь к исходникам."""
    return get_project_root() / 'src'


def get_project_root() -> Path:
    """Возвращает путь к корню проекта."""
    PROJECT_NAME: Final = 'Lab_5'
    current_path = Path(__file__).resolve()
    while current_path.parts[-1] != PROJECT_NAME:
        if current_path.parent == current_path:
            raise FileNotFoundError(f"Корень проекта {PROJECT_NAME} не найден.")
        current_path = current_path.parent
    return current_path
