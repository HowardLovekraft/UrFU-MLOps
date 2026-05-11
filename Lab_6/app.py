from fastapi import FastAPI
import pandas as pd

from schemas import RecordSchema, PredictionSchema
from train import pipeline


app = FastAPI()


@app.post('/predict')
def predict(data: RecordSchema) -> PredictionSchema:
    obj = pd.DataFrame(data.model_dump)
    pred = pipeline.predict(obj)
    return PredictionSchema(performance_index=pred)
