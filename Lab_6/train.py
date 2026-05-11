from pathlib import Path

import kagglehub
from loguru import logger
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.metrics import classification_report
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, OrdinalEncoder
from sklearn.preprocessing import StandardScaler
from xgboost import XGBClassifier


DATASET_NAME = "uniquetech/air-quality-and-student-performance-dataset"
data_path = Path(kagglehub.dataset_download(DATASET_NAME))
data = pd.read_csv(data_path / 'student_learning_air_quality.csv')


# Дропаем индекс из датасета
data = data.drop(columns=['student_id'])
cols_to_drop: set[str] = set()

air_quality_mapping = {'Poor': 0, 'Moderate': 1, 'Good': 2}
data['air_quality'] = data.air_quality_label.map(air_quality_mapping)
data.drop(columns=['air_quality_label'], inplace=True)

performance_mapping = {'Low': 0, 'Medium': 1, 'High': 2}
data['target'] = data.performance_label.map(performance_mapping)
data.drop(columns=['performance_label'], inplace=True)


X_train, X_test, y_train, y_test = train_test_split(
    data.drop(columns=['target', 'quiz_score']),
    data.target,
    test_size=0.3, random_state=42
)

param = {
    'max_depth': 2,
    'n_estimators': 13
}

cols_to_onehot = ['subject']
cols_to_ordinal = ['day', 'period', 'grade']
col_transformer = ColumnTransformer(
    [
        ('one-hot', OneHotEncoder(drop='first', sparse_output=False, handle_unknown='ignore'), cols_to_onehot),
        ('ordinal', OrdinalEncoder(), cols_to_ordinal)
    ],
    remainder='passthrough'
)

pipeline = Pipeline([
    ('preprocessor', col_transformer),
    ('scaler', StandardScaler()),
    ('model', XGBClassifier(**param))
])
pipeline.fit(X_train, y_train)

y_pred = pipeline.predict(X_test)
metrics = str(classification_report(y_test, y_pred))
logger.info(metrics)
