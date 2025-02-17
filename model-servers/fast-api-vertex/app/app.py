# FastAPI model server for Iris dataset
# Path: model-servers/fast-api-server/app/app.py
# Run with: uvicorn app:app --reload

import os
import joblib
import numpy as np
import uvicorn
from fastapi import FastAPI
from pydantic import BaseModel
from typing import List

# Load the trained model
with open("model.pkl", "rb") as f:
    model = joblib.load(f)

# Initialize FastAPI app
app = FastAPI()

# Define environment variables with defaults
HEALTH_ROUTE = os.getenv("AIP_HEALTH_ROUTE", "/health")
PREDICT_ROUTE = os.getenv("AIP_PREDICT_ROUTE", "/predict")

class IrisData(BaseModel):
    sepal_length: float
    sepal_width: float
    petal_length: float
    petal_width: float
    

# Define Pydantic models for request and response validation
class PredictRequest(BaseModel):
    # TODO: Define the instances field

class PredictResponse(BaseModel):
    # TODO: Define the predictions field

@app.get("/", summary="Root Endpoint")
async def root():
    return {"message": "This is an API for the Iris dataset"}

@app.get(HEALTH_ROUTE, status_code=200, summary="Health Check")
def health():
    return {"status": "ok"}

@app.post(PREDICT_ROUTE, response_model=PredictResponse, summary="Make a Prediction")
async def predict(request: PredictRequest):
    # TODO: Extract the instances from the request, make a prediction, and return the response

# Run the API
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8080)
