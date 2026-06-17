[Versión en español](README_es.md)

# Flask CI/CD Demo

A minimal Python web application built with Flask, containerised with Docker, and automatically deployed to Azure using a GitHub Actions CI/CD pipeline.

## Project description

This project demonstrates a complete continuous integration and deployment (CI/CD) cycle for a containerised web application. Any push to the `main` branch automatically triggers three sequential jobs:

1. **test** — unit tests are executed with `pytest` to ensure the application works correctly before building the image.
2. **build-and-push** — the Docker image is built and pushed to Azure Container Registry (ACR).
3. **deploy** — the image is deployed to Azure Container Instances (ACI), replacing the previous container.

The result is an always up-to-date application, publicly accessible on Azure, with no manual intervention required.

## Prerequisites

- Python 3.11+
- [`uv`](https://docs.astral.sh/uv/) (recommended) **or** `pip`
- [Docker](https://www.docker.com/) — optional, for local container testing
- Active Azure subscription (only needed to run the pipeline)

## Installation

### Recommended — uv

```bash
uv venv .venv
source .venv/bin/activate        # macOS/Linux
source .venv/Scripts/activate    # Windows Git Bash
.venv\Scripts\Activate.ps1       # Windows PowerShell
uv pip install -r requirements.txt
```

### Alternative — pip

```bash
python -m venv .venv
source .venv/bin/activate        # macOS/Linux
source .venv/Scripts/activate    # Windows Git Bash
.venv\Scripts\Activate.ps1       # Windows PowerShell
pip install -r requirements.txt
```

## Run locally

```bash
python app.py
```

Open <http://localhost:5000> in your browser. You should see:

```
¡Hola! Soy una aplicación desplegada con CI/CD.
```

## Run tests

```bash
pytest          # run all tests
pytest -q       # quiet output (matches CI)
pytest tests/test_app.py::test_root   # single test
```

Tests use Flask's `test_client()` directly against the `app` object — no running server needed.

## Docker

### Build the image locally

```bash
docker build -t flask-cicd .
```

### Run in the foreground

```bash
docker run --rm -p 5000:5000 flask-cicd
```

Stop with `Ctrl+C`. Open <http://localhost:5000>.

### Run in the background

```bash
docker run -d --name flask-cicd -p 5000:5000 flask-cicd
```

### View logs / stop / remove

```bash
docker logs flask-cicd
docker stop flask-cicd
docker rm flask-cicd
```

### Run the published image from Azure Container Registry

```bash
# Authenticate with ACR
az acr login --name acrentregable4202606

# Pull and run the image for a specific workflow run
docker run --rm -p 5000:5000 \
  acrentregable4202606.azurecr.io/flask-entregable4:<RUN_NUMBER>
```

Replace `<RUN_NUMBER>` with the GitHub Actions run number (visible in the *Actions* tab of the repository).

## CI/CD pipeline

The `.github/workflows/ci-cd.yml` file triggers on every push to `main` and runs three sequential jobs:

### Job 1 — test

- Checks out the code.
- Installs Python 3.11 using `actions/setup-python@v5`.
- Installs dependencies from `requirements.txt`.
- Runs `pytest -q` and blocks the pipeline if any test fails.

### Job 2 — build-and-push

- Logs in to Azure using the `AZURE_CREDENTIALS` secret.
- Authenticates with ACR.
- Builds the Docker image tagged as `<acrName>.azurecr.io/flask-entregable4:<run_number>`.
- Pushes the image to ACR.

### Job 3 — deploy

- Deletes the previous ACI container (if any) to avoid conflicts.
- Creates a new Azure Container Instance with the freshly published image.
- Assigns a dynamic DNS label in the format `flask<run_number>`.
- Prints the public URL at the end of the job.

### Required secret

The only credential required is set in *Settings → Secrets and variables → Actions*:

| Secret | Description |
|---|---|
| `AZURE_CREDENTIALS` | Azure service principal JSON |

To create the service principal:

```bash
az ad sp create-for-rbac --name "github-actions-sp" \
  --role contributor \
  --scopes /subscriptions/<SUBSCRIPTION_ID>/resourceGroups/rg-entregable4 \
  --sdk-auth
```

Copy the JSON output and save it as the `AZURE_CREDENTIALS` secret.

### Workflow variables

Non-sensitive values are defined as `env:` at the top of the workflow file:

| Variable | Value |
|---|---|
| `ACR_NAME` | `acrentregable4202606` |
| `IMAGE_NAME` | `flask-entregable4` |
| `ACI_NAME` | `aci-entregable4` |
| `RESOURCE_GROUP` | `rg-entregable4-github` |
| `LOCATION` | `westeurope` |
| `CONTAINER_PORT` | `5000` |

The image tag and DNS label use `${{ github.run_number }}`.

## Deployed application

After each successful pipeline run, Azure automatically assigns a public URL to the container in the format:

```
http://flask<RUN_NUMBER>.westeurope.azurecontainer.io:5000
```

where `<RUN_NUMBER>` is the numeric GitHub Actions run number. The exact URL is printed at the end of the **deploy** job in the Actions console.

## Architecture

```
GitHub (push to main)
        │
        ▼
GitHub Actions (.github/workflows/ci-cd.yml)
  ├── test          → pytest on source code
  ├── build-and-push → Docker image → ACR (acrentregable4202606)
  └── deploy        → ACI (aci-entregable4) in westeurope
                           │
                           ▼
               http://flask<RUN_NUMBER>.westeurope.azurecontainer.io:5000
```

### Key files

| File | Purpose |
|---|---|
| `app.py` | Flask app — single `GET /` endpoint |
| `requirements.txt` | Dependencies: `flask` and `pytest` |
| `Dockerfile` | Image based on `python:3.11-slim` |
| `tests/test_app.py` | Unit test for the root endpoint |
| `.github/workflows/ci-cd.yml` | Full CI/CD pipeline |
