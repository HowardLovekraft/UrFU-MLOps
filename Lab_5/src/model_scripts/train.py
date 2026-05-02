from typing import Any

import mlflow
from mlflow.models import infer_signature
import numpy as np
import pandas as pd
import pickle
from sklearn.preprocessing import StandardScaler, PowerTransformer
from sklearn.linear_model import SGDRegressor
from sklearn.model_selection import GridSearchCV
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.pipeline import Pipeline


def eval_metrics(actual, pred):
    rmse = np.sqrt(mean_squared_error(actual, pred))
    mae = mean_absolute_error(actual, pred)
    r2 = r2_score(actual, pred)
    return rmse, mae, r2


def scale_frame(frame: pd.DataFrame, target: str ="Amount"):
    df = frame.copy()
    X, y = df.drop(columns = [target]), df[target]

    with open('x_train', "w") as f:
        f.write(str(X.to_numpy()))

    scaler = StandardScaler()
    power_trans = PowerTransformer()
    X_scale = scaler.fit_transform(X.values)
    Y_scale = power_trans.fit_transform(y.values.reshape(-1,1))
    return X_scale, Y_scale, power_trans


def train(cfg: dict[str, Any], target: str = 'Amount'):
    df_train = pd.read_csv(cfg['data_split']['trainset_path'])
    df_test = pd.read_csv(cfg['data_split']['testset_path'])
    print(df_train.shape)

    X_train, y_train = df_train.drop(columns=[target]).values, df_train[target].values
    X_val, y_val = df_test.drop(columns=[target]).values, df_test[target].values
    power_trans = PowerTransformer()
    y_train = power_trans.fit_transform(y_train.reshape(-1, 1))
    y_val = power_trans.transform(y_val.reshape(-1, 1))

    mlflow.set_experiment("Linear model Chocolate sales")
    with mlflow.start_run():
        lr_pipe = Pipeline([
            ('scaler', StandardScaler()),
            ('model', SGDRegressor(random_state=42))
        ])
        params = {
            'model__alpha': cfg['train']['alpha'],
            'model__fit_intercept': [False, True],
        }

        clf = GridSearchCV(lr_pipe, params, cv = cfg['train']['cv'], n_jobs=4)
        clf.fit(X_train, y_train.reshape(-1))
        best = clf.best_estimator_
        best_lr = best['model']

        y_pred = best.predict(X_val)
        y_price_pred = power_trans.inverse_transform(y_pred.reshape(-1, 1))
        print(f'y_price_pred: {y_price_pred[:5]}')
        print(f'y_val: {y_val[:5]}')

        (rmse, mae, r2) = eval_metrics(power_trans.inverse_transform(y_val.reshape(-1, 1)), y_price_pred.reshape(-1, 1))
        mlflow.log_metric("rmse", rmse)
        mlflow.log_metric("r2", r2)
        mlflow.log_metric("mae", mae)
        print(
            [f"R2: {r2}", f"RMSE: {rmse}", f"MAE: {mae}"], sep='\n'
        )

        preds = best.predict(X_train)
        signature = infer_signature(X_train, preds)
        mlflow.sklearn.log_model(best, "model", signature=signature)

        with open(cfg['train']['model_path'], "wb") as file:
            pickle.dump(best, file)

        with open(cfg['train']['power_path'], "wb") as file:
            pickle.dump(power_trans, file)
