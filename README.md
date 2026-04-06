# MLOps course code repository

## Prerequisites

### Install uv

**macOS / Linux:**

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

**Windows (PowerShell):**

```powershell
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

After installing, restart your terminal so the `uv` command is available.

### Install dependencies

Install the core dependencies:

```bash
uv sync
```

Install a specific module (e.g. model-servers):

```bash
uv sync --extra model-servers
```

Install everything except Vertex AI:

```bash
uv sync --extra all
```

Install with Vertex AI (requires GCP credentials):

```bash
uv sync --extra all --extra vertex
```

> **Note:** Vertex AI is kept as a separate extra because it pulls in GCP-specific
> dependencies that are only needed if you are deploying to Google Cloud.

---

## Model servers

### FastAPI

#### Fast-api-tutorial

```bash
cd model-servers/fast-api-tutorial/
uv run python app/app.py
```

Now the FastAPI server is running on `http://localhost:8000`.

To access the API documentation, go to `http://localhost:8000/docs`.

![FastAPI swagger](imgs/fast-api-swagger.png)

Now you can try the model server by sending a POST request to `http://localhost:8000/predict` with the following payload:

```json
{
  "sepal_length": 0,
  "sepal_width": 0,
  "petal_length": 0,
  "petal_width": 0
}
```

Using curl:

```bash
curl -X 'POST' \
  'http://localhost:8000/predict' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{
  "sepal_length": 0,
  "sepal_width": 0,
  "petal_length": 0,
  "petal_width": 0
}'
```

Or using Python:

```python
import requests

url = "http://localhost:8000/predict"

payload = {
  "sepal_length": 0,
  "sepal_width": 0,
  "petal_length": 0,
  "petal_width": 0
}
headers = {
  'accept': 'application/json',
  'Content-Type': 'application/json'
}

response = requests.request("POST", url, headers=headers, json=payload)

print(response.text)
```

Or using the "Try it out" button in the API documentation.

### MLServer

MLServer is a model server that allows you to deploy models in a production environment. It is a high-performance model server that can serve models in real-time.
MLServer is not compatible with Windows.
Use Linux or macOS. Alternatively, you can use WSL2 on Windows or Google Colab.

To use it on Google Colab, open the notebook on the Google Colab interface.
Upload the model.pkl file to the Colab environment.
Run the notebook cells.

---

## Model Registry

MLFlow is a model registry that allows you to track and manage models. It is a tool that allows you to manage the full lifecycle of a model, from experimentation to deployment.

```bash
uv sync --extra model-registry
```

`model-registry/mlflow-basics.ipynb` contains the basic tutorial.

`model-registry/mlflow-training.ipynb` contains the training tutorial.

To run the MLflow server:

```bash
uv run mlflow ui --port 5001 --host 0.0.0.0
```

---

## Pipelines

Pipelines are a way to automate the machine learning workflow. They allow you to create a sequence of steps that can be executed in a specific order.
Metaflow is a tool that allows you to create pipelines in Python.
Currently, there is no support for Windows, so you need to use Linux or macOS. Alternatively, you can use WSL2 on Windows or Google Colab.

```bash
uv sync --extra pipelines
```

`pipelines/metaflow-basics.ipynb` contains the basic tutorial.
`pipelines/metaflow-model-training.ipynb` contains the training exercise.
