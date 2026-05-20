import google.cloud.aiplatform as aiplatform

PROJECT_ID = "pruebaedem"
REGION = "us-central1"
IMAGE_URI = f"{REGION}-docker.pkg.dev/{PROJECT_ID}/vertex-repo/fastapi-app-vertex:latest"
MODEL_DISPLAY_NAME = "fastapi-iris-model"
ENDPOINT_DISPLAY_NAME = "fastapi-iris-endpoint"

aiplatform.init(project=PROJECT_ID, location=REGION)

# 1. Register model in Vertex AI Model Registry
print("Registering model in Model Registry...")
model = aiplatform.Model.upload(
    display_name=MODEL_DISPLAY_NAME,
    serving_container_image_uri=IMAGE_URI,
    serving_container_predict_route="/predict",
    serving_container_health_route="/health",
    serving_container_ports=[8080],
    serving_container_environment_variables={
        "AIP_HEALTH_ROUTE": "/health",
        "AIP_PREDICT_ROUTE": "/predict",
        "AIP_PORT": "8080",
    },
)
print(f"Model registered: {model.resource_name}")

# 2. Create endpoint
print("Creating endpoint...")
endpoint = aiplatform.Endpoint.create(display_name=ENDPOINT_DISPLAY_NAME)
print(f"Endpoint created: {endpoint.resource_name}")

# 3. Deploy model to endpoint
print("Deploying model to endpoint (this may take ~10 minutes)...")
model.deploy(
    endpoint=endpoint,
    machine_type="n1-standard-2",
    min_replica_count=1,
    max_replica_count=1,
    traffic_percentage=100,
)
print(f"Model deployed successfully!")
print(f"Endpoint resource name: {endpoint.resource_name}")
print(f"To predict, use endpoint: {endpoint.resource_name}")
