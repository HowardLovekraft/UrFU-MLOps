from pathlib import Path
from typing import Callable, Final


def fixdir(func: Callable[[], Path]):
    """Создает директорию, если её не существует."""
    def wrapper() -> Path:
        dir_path = func()
        if dir_path:
            dir_path.mkdir(parents=True, exist_ok=True)
        return dir_path
    return wrapper


def get_project_root() -> Path:
    """Возвращает путь к корню проекта."""
    PROJECT_NAME: Final = "Lab_6"
    current_path = Path(__file__).resolve()
    while current_path.parts[-1] != PROJECT_NAME:
        if current_path.parent == current_path:
            raise FileNotFoundError(f"Корень проекта {PROJECT_NAME} не найден.")
        current_path = current_path.parent
    return current_path


@fixdir
def get_weights_dpath() -> Path:
    """Возвращает путь до директории весов модели."""
    return get_project_root() / 'weights'


def get_model_weights_path() -> Path:
    """Возвращает путь до весов обученной модели."""
    return get_weights_dpath() / 'model.pkl'
