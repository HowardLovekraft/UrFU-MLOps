from typing import NamedTuple
import warnings

import matplotlib.pyplot as plt
from loguru import logger
import mlflow
from mlflow.models import infer_signature
import pandas as pd
import seaborn as sns
from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.ensemble import RandomForestClassifier
from sklearn.naive_bayes import GaussianNB
from sklearn.linear_model import LogisticRegression
from sklearn.svm import SVC
from sklearn.neural_network import MLPClassifier
from sklearn.metrics import accuracy_score, recall_score, precision_score
from sklearn.metrics import f1_score, classification_report, roc_curve
from sklearn.metrics import roc_auc_score, confusion_matrix
from sklearn.neural_network._multilayer_perceptron import ConvergenceWarning


def calc_metrics(y_val, y_pred) -> dict[str, float]:
    accuracy = accuracy_score(y_val, y_pred)
    recall = recall_score(y_val, y_pred)
    precision = precision_score(y_val, y_pred)
    f1_metric = f1_score(y_val, y_pred)
    roc_auc = roc_auc_score(y_val, y_pred, average=None)

    return {
        'accuracy': round(accuracy, 5),
        'recall': round(recall, 5),
        'precision': round(precision, 5),
        'f1': round(f1_metric, 5),
        'roc_auc': round(roc_auc, 5)
    }


warnings.filterwarnings("ignore", category=ConvergenceWarning)

logger.info("Датасет загружается...")

data = pd.read_csv("GoT_preprocessed_data.csv", index_col="S.No")
target = pd.read_csv("GoT_target.csv", index_col="S.No")

assert (data.shape[0] == 1557 and target.shape[0] == 1557), "Размер датасета не соотв. исходному"
    
X = data
y = target.to_numpy().flatten()

# 70% - трейн, 30% - валидация+тест
X_train, X_val, y_train, y_val = train_test_split(X, y, test_size=0.7, random_state=42)  

mlp_param_grid = (
    {
        'activation' : ['relu'],
        'solver' : ['adam'],
        'hidden_layer_sizes': [
            (100,), (13,), (13, 1), (13, 13, 1), (20,), (3,), (5,)
        ],
        'max_iter': [100, 600, 2000, 10000],
        'random_state': [1337]
    }
)

models = {
    'Naive Bayes': GaussianNB(),
    'Random Forest (Estim=5)': RandomForestClassifier(5, random_state=1337),
    'Random Forest (Estim=10)': RandomForestClassifier(10, random_state=1337),
    'Random Forest (Estim=20)': RandomForestClassifier(20, random_state=1337),
    'Random Forest (Estim=50)': RandomForestClassifier(50, random_state=1337),
    'Logistic Regression (L1)': LogisticRegression(l1_ratio=1, solver='liblinear'),
    'Logistic Regression (L2)': LogisticRegression(l1_ratio=0),
    'Support Vector (C=0,5)': SVC(C=0.5),
    'Support Vector (C=1,0)': SVC(C=1.0),
    'Support Vector (C=2,0)': SVC(C=2.0),
    # Выбираем лучшую архитектуру MLP по метрике ROC-AUC
    'MultiLayer Perceptron': GridSearchCV(MLPClassifier(), mlp_param_grid, cv=3, scoring='roc_auc')
}

metrics = ('Accuracy', 'Recall', 'Precision', 'F1', 'ROC-AUC')

logger.info("Начат эксперимент в MLflow...")
mlflow.set_experiment("Game of Thrones Deaths")

# Учим модели
for model_name, model in models.items():
    with mlflow.start_run(run_name=f"train_{model_name}"):
        logger.info(f"Начато обучение модели {model_name}...")
        model.fit(X_train, y_train)
        logger.info("Обучение модели завершено")
        
        y_pred = model.predict(X_val)
        model_metrics = calc_metrics(y_val, y_pred)
        mlflow.log_metrics(model_metrics)
    
        for param in ["n_estimators", "C", "l1_ratio", 'hidden_layer_sizes']:
            if hasattr(model, param):
                mlflow.log_param(param, getattr(model, param))

        signature = infer_signature(X_val, y_val)
        mlflow.sklearn.log_model(model, signature=signature, name=f"model_{model_name}")
            