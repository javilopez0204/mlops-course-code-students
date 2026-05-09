# MLOps course code repository

Hands-on material for the MLOps course: model serving (FastAPI, MLServer),
model registry (MLflow), pipelines (Metaflow, Kubeflow) and deployment to
Google Cloud Vertex AI.

## Table of contents

- [Prerequisites](#prerequisites)
  - [Install uv](#install-uv)
  - [Install the Google Cloud SDK (`gcloud`)](#install-the-google-cloud-sdk-gcloud)
  - [Install dependencies](#install-dependencies)
- [Repository layout](#repository-layout)
- [Model servers](#model-servers)
  - [FastAPI](#fastapi)
  - [MLServer](#mlserver)
  - [FastAPI on Vertex AI (Docker)](#fastapi-on-vertex-ai-docker)
- [Model Registry (MLflow)](#model-registry-mlflow)
- [Pipelines](#pipelines)
  - [Metaflow](#metaflow)
  - [Kubeflow](#kubeflow)
- [Vertex AI Pipelines (final assignment)](#vertex-ai-pipelines-final-assignment)

---

## Prerequisites

### Install uv

[`uv`](https://docs.astral.sh/uv/) is the Python package & project manager
used in this repository.

**macOS / Linux:**

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

**Windows (PowerShell):**

```powershell
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

After installing, restart your terminal so the `uv` command is available.

Reference: [uv installation docs](https://docs.astral.sh/uv/getting-started/installation/).

### Install the Google Cloud SDK (`gcloud`)

The `gcloud` CLI is required for the Vertex AI parts of the course
(pushing Docker images to Artifact Registry, running pipelines on Vertex
AI, accessing GCS buckets, etc.).

Official installation guide: <https://cloud.google.com/sdk/docs/install>

**macOS** (recommended via Homebrew):

```bash
brew install --cask google-cloud-sdk
```

Or follow the manual installer: <https://cloud.google.com/sdk/docs/install#mac>

**Linux:**

```bash
curl -O https://dl.google.com/dl/cloudsdk/channels/rapid/install_google_cloud_sdk.bash
bash install_google_cloud_sdk.bash
```

Or follow: <https://cloud.google.com/sdk/docs/install#linux>

**Windows:**

Download and run the installer from
<https://cloud.google.com/sdk/docs/install#windows>.

#### Initialise and authenticate

After installing, restart your terminal and run:

```bash
gcloud init
gcloud auth login
gcloud auth application-default login
gcloud config set project YOUR_PROJECT_ID
```

Enable the APIs used in the course:

```bash
gcloud services enable \
  artifactregistry.googleapis.com \
  aiplatform.googleapis.com \
  storage.googleapis.com \
  cloudbuild.googleapis.com
```

Useful references:

- [Initialising the gcloud CLI](https://cloud.google.com/sdk/docs/initializing)
- [Authorising the gcloud CLI](https://cloud.google.com/sdk/docs/authorizing)
- [Application Default Credentials (ADC)](https://cloud.google.com/docs/authentication/provide-credentials-adc)
- [Vertex AI documentation](https://cloud.google.com/vertex-ai/docs)
- [Artifact Registry documentation](https://cloud.google.com/artifact-registry/docs)
- [Cloud Storage documentation](https://cloud.google.com/storage/docs)

> If you are running on Apple Silicon and plan to push Docker images to
> Artifact Registry, also make sure
> [Docker Desktop](https://www.docker.com/products/docker-desktop/) is
> installed and running.

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

## Repository layout

```text
.
├── model-servers/        # FastAPI, MLServer, FastAPI + Vertex AI examples
├── model-registry/       # MLflow notebooks and tracking DB
├── pipelines/            # Metaflow and Kubeflow notebooks
├── entregable/           # Final assignment: Vertex AI pipelines
├── imgs/                 # Images used in the README and notebooks
├── pyproject.toml        # uv project definition with extras
└── uv.lock
```

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

The examples live in `model-servers/mlserver/`:

- `00-basic` — minimal scikit-learn model deployed with MLServer.
- `01-custom` — custom runtime example.

To run the basic example locally:

```bash
cd model-servers/mlserver/00-basic
uv run mlserver start .
```

To use it on Google Colab, open the notebook in the Colab interface, upload
the `model.pkl` file to the Colab environment and run the notebook cells.

### FastAPI on Vertex AI (Docker)

The folder `model-servers/fast-api-vertex/` contains a FastAPI app packaged
to be served as a custom container on
[Vertex AI Prediction](https://cloud.google.com/vertex-ai/docs/predictions/use-custom-container).

Build and run the container locally:

```bash
cd model-servers/fast-api-vertex
bash docker-instructions.sh
```

Push the image to Google Cloud Artifact Registry:

```bash
# 1. Edit push-docker-gcp.sh and set PROJECT_ID, REGION and REPO_NAME.
# 2. Make sure gcloud is authenticated:
gcloud auth login
gcloud auth configure-docker REGION-docker.pkg.dev

# 3. Push the image:
bash push-docker-gcp.sh
```

References:

- [Create an Artifact Registry repository](https://cloud.google.com/artifact-registry/docs/repositories/create-repos)
- [Deploy a model with a custom container on Vertex AI](https://cloud.google.com/vertex-ai/docs/predictions/use-custom-container)

---

## Model Registry (MLflow)

MLflow is a model registry that allows you to track and manage models. It is a tool that allows you to manage the full lifecycle of a model, from experimentation to deployment.

```bash
uv sync --extra model-registry
```

- `model-registry/mlflow-basics.ipynb` contains the basic tutorial.
- `model-registry/mlflow-training.ipynb` contains the training tutorial.

To run the MLflow server:

```bash
uv run mlflow ui --port 5001 --host 0.0.0.0
```

Then open <http://localhost:5001>.

---

## Pipelines

### Metaflow

Pipelines are a way to automate the machine learning workflow. They allow you to create a sequence of steps that can be executed in a specific order.
Metaflow is a tool that allows you to create pipelines in Python.
Currently, there is no support for Windows, so you need to use Linux or macOS. Alternatively, you can use WSL2 on Windows or Google Colab.

```bash
uv sync --extra pipelines
```

- `pipelines/metaflow-basics.ipynb` — basic tutorial.
- `pipelines/metaflow-model-training.ipynb` — training exercise.
- `pipelines/metaflow_trainingflow.py` — runnable Metaflow flow:

```bash
cd pipelines
uv run python metaflow_trainingflow.py run
```

### Kubeflow

[Kubeflow Pipelines](https://www.kubeflow.org/docs/components/pipelines/) is
the open-source pipeline framework that powers Vertex AI Pipelines.

- `pipelines/kubeflow_tutorial.ipynb` — introduction to KFP components and pipelines.
- `pipelines/kubeflow_exercise.ipynb` — exercise to complete.
- `pipelines/kubeflow_exercise_SOLUTION.ipynb` — reference solution.

The KFP SDK is installed as part of the `vertex` extra:

```bash
uv sync --extra vertex
```

---

## Vertex AI Pipelines (final assignment)

The final assignment lives in `entregable/vertexai-pipelines.ipynb` and
shows how to compile and run a Kubeflow pipeline on
[Vertex AI Pipelines](https://cloud.google.com/vertex-ai/docs/pipelines/introduction).

Before running the notebook:

1. Install the Vertex AI extra:

   ```bash
   uv sync --extra all --extra vertex
   ```

2. Make sure `gcloud` is installed and authenticated (see
   [Install the Google Cloud SDK](#install-the-google-cloud-sdk-gcloud)).

3. Set up Application Default Credentials so the SDK can talk to GCP:

   ```bash
   gcloud auth application-default login
   ```

4. Edit the first cell of the notebook and set:

   - `PROJECT_ID` — your GCP project ID.
   - `REGION` — e.g. `us-central1`.
   - `BUCKET_NAME` — name of a GCS bucket the pipeline will use as its root.

Useful references:

- [Vertex AI Pipelines overview](https://cloud.google.com/vertex-ai/docs/pipelines/introduction)
- [Build a pipeline with the KFP SDK](https://cloud.google.com/vertex-ai/docs/pipelines/build-pipeline)
- [Run a pipeline on Vertex AI](https://cloud.google.com/vertex-ai/docs/pipelines/run-pipeline)
- [Vertex AI pricing](https://cloud.google.com/vertex-ai/pricing)
