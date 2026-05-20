# FastAPI model server for Iris dataset
# Path: model-servers/fast-api-vertex-cloud-build/app/app.py
# Run with: uvicorn app:app --reload

import os
import joblib
import uvicorn
from fastapi import FastAPI
from pydantic import BaseModel
from typing import List

# Load the trained model
try:
    with open("model.pkl", "rb") as f:
        model = joblib.load(f)
except Exception as e:
    print(f"Error loading model: {e}")

    # Create a default model mock
    class MockModel:
        def predict(self, inputs):
            import random
            return [random.randint(0, 2) for _ in range(len(inputs))]
    model = MockModel()
    print("Using default model mock")

# Initialize FastAPI app
app = FastAPI()
print("HOla buenos dias Javitobirras")

# Define environment variables with defaults
HEALTH_ROUTE = os.getenv("AIP_HEALTH_ROUTE", "/health")
PREDICT_ROUTE = os.getenv("AIP_PREDICT_ROUTE", "/predict")


class IrisData(BaseModel):
    sepal_length: float
    sepal_width: float
    petal_length: float
    petal_width: float


class PredictRequest(BaseModel):
    instances: List[IrisData]


class PredictResponse(BaseModel):
    predictions: List[int]


@app.get("/", summary="Root Endpoint")
async def root():
    return {"message": "This is an API for the Iris dataset"}


@app.get(HEALTH_ROUTE, status_code=200, summary="Health Check")
def health():
    return {"status": "ok"}


@app.post(PREDICT_ROUTE, response_model=PredictResponse, summary="Make a Prediction")
async def predict(request: PredictRequest):
    inputs = [
        [x.sepal_length, x.sepal_width, x.petal_length, x.petal_width]
        for x in request.instances
    ]
    y_pred = model.predict(inputs)
    outputs = [int(x) for x in y_pred]
    return PredictResponse(predictions=outputs)


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8080)
