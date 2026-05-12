from fastapi import FastAPI
import joblib
import pandas as pd
import uvicorn

from src.db import create_table, get_record, add_record
from src.paths import get_model_weights_path
from src.schemas import RecordSchema, PredictionSchema


create_table()
model = joblib.load(get_model_weights_path())
app = FastAPI(title='Perf')


@app.get('/')
def greating():
    return 'Hello World!'

@app.post('/predict', response_model=PredictionSchema)
def predict(data: RecordSchema) -> dict[str, int]:
    record = get_record(data)
    if record is not None:
        pred = record
    else:
        obj = pd.DataFrame(data.model_dump(mode='json'), index=[1])
        pred = model.predict(obj)[0]
        add_record(data, pred)
    return {'performance_index': pred}


if __name__ == '__main__':
    uvicorn.run(app, host="0.0.0.0", port=8000)
