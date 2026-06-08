# Churn Prediction Service — Detailed README

## Project Summary

This repository implements a churn prediction service and ML pipeline. It includes data preparation, feature engineering, training, model artifacts (MLflow), and a FastAPI-based serving component. The project is CI/CD-enabled to automatically build, test, and publish a Docker image for production deployment.

## Quick Links

- Docker image: `00pizzalover00/churn-service`
- Docker tags: https://hub.docker.com/repository/docker/00pizzalover00/churn-service/tags
- CI workflow: [.github/workflows/ci.yml](.github/workflows/ci.yml)
- Main code and app layout: [src/](src/)
- Serving code: [src/serving/inference.py](src/serving/inference.py)
- Model artifacts and tracked runs: [mlruns/](mlruns/)

## Dataset

This project uses the "Telco Customer Churn" dataset from Kaggle: https://www.kaggle.com/datasets/blastchar/telco-customer-churn

Brief description:

- Source: Kaggle — "Telco Customer Churn" dataset.
- Size: ~7,043 customer records and ~21 columns (customer attributes and account information).
- Key columns: `customerID`, `gender`, `SeniorCitizen`, `Partner`, `Dependents`, `tenure`, `PhoneService`, `MultipleLines`, `InternetService`, `OnlineSecurity`, `OnlineBackup`, `DeviceProtection`, `TechSupport`, `StreamingTV`, `StreamingMovies`, `Contract`, `PaperlessBilling`, `PaymentMethod`, `MonthlyCharges`, `TotalCharges`, `Churn`.
- Target: `Churn` — indicates whether the customer left (`Yes`) or stayed (`No`).
- Notes: dataset requires minimal cleaning (for example, `TotalCharges` may contain missing/blank entries); typical preprocessing includes type conversion, imputation, encoding categorical variables, and aligning feature columns prior to serving.

Full dataset details and download: [Telco Customer Churn (Kaggle)](https://www.kaggle.com/datasets/blastchar/telco-customer-churn)


## Table of Contents

- Project Summary
- System Architecture Overview
- CI/CD Pipeline (how it works)
- Docker Hub image and usage
- Getting the code (GitHub)
- Local development and running the app
- Running with Docker
- Tests
- Model artifacts & MLflow
- Project structure
- Contributing & support


## 🧩 System Architecture Overview

This system moves ML code from development to production via an automated pipeline. The main components:

- Source control: GitHub repository (this repo).
- CI: GitHub Actions (see [.github/workflows/ci.yml](.github/workflows/ci.yml)). The pipeline runs on every push and/or pull request depending on the workflow triggers.
- Containerization: Docker image `00pizzalover00/churn-service` built by CI and pushed to Docker Hub.
- Model tracking & artifacts: MLflow artifacts and model metadata stored in `mlruns/` and packaged into the container image or separate model artifact storage depending on CI config.
- Serving: FastAPI application exposing prediction endpoints. The app reads the serialized model and `feature_columns.json` to ensure features align.
- Deployment target: Any container platform (Docker Compose, Kubernetes, AWS ECS, Azure ACI, etc.). The repository provides a deployable image on Docker Hub.


## 🏗️ CI/CD Pipeline — What happens on push

The repository contains a GitHub Actions CI workflow at [.github/workflows/ci.yml](.github/workflows/ci.yml). Typical stages performed by the workflow:

1. Checkout the repository.
2. Set up Python environment and install dependencies from `requirements.txt`.
3. Run unit and integration tests using `pytest`.
4. Run linting/static checks (optional, if configured).
5. Build the application Docker image.
6. Tag the Docker image (for example, `latest` and commit-based tag or semantic version).
7. Authenticate with Docker Hub using repo secrets (for example: `DOCKER_USERNAME` / `DOCKER_PASSWORD` or `DOCKERHUB_TOKEN`).
8. Push the image to Docker Hub at `00pizzalover00/churn-service`.
9. Optionally save/upload build artifacts and model files to MLflow, remote storage, or GitHub Releases.

Secrets and environment variables required by CI (examples):

- `DOCKER_USERNAME` / `DOCKER_PASSWORD` (or `DOCKERHUB_TOKEN`) — for pushing images.
- `MLFLOW_TRACKING_URI` and `MLFLOW_S3_BUCKET` (if pushing models remotely).

Refer to the workflow file for exact steps and secret names: [.github/workflows/ci.yml](.github/workflows/ci.yml)


## Docker Hub — Image and Tags

Official image name: `00pizzalover00/churn-service`

Pull the image from Docker Hub:

```
docker pull 00pizzalover00/churn-service:latest
```

Browse available tags here:

https://hub.docker.com/repository/docker/00pizzalover00/churn-service/tags

Notes on tags:
- `latest` typically contains the most recently published build from `main` or a release branch.
- CI may push commit-specific tags or semver tags depending on your CI configuration.


## How to get the code (GitHub)

Clone the repository to your machine:

```
git clone <REPO_URL>
cd <REPO_FOLDER>
```

Replace `<REPO_URL>` with the repository's HTTPS or SSH URL.


## Local development — Python (recommended)

1. Create and activate a virtual environment (example using `venv`):

```bash
python -m venv .venv
# Windows
.venv\Scripts\activate
# macOS/Linux
source .venv/bin/activate
```

2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Run tests:

```bash
pytest -q
```

4. Run the API locally (FastAPI / Uvicorn). There are two common entrypoints depending where you run from:

- If running from the repository root and `src` is the Python package root:

```bash
uvicorn src.app.main:app --reload --host 0.0.0.0 --port 8000
```

- If the top-level `app` package is used, run:

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Open http://localhost:8000/docs to view the interactive API docs (if the app exposes them via FastAPI).


## Running with Docker

Run the official Docker image from Docker Hub:

```bash
docker run --rm -p 8000:8000 00pizzalover00/churn-service:latest
```

This runs the container and exposes the app on port 8000. Adjust port mapping as needed.

To build locally and run (useful for development):

```bash
docker build -t local-churn-service:dev .
docker run --rm -p 8000:8000 local-churn-service:dev
```


## Tests

- Unit and integration tests are located in the `tests/` directory.
- Use `pytest` to run tests:

```bash
pytest tests/ -q
```

- CI runs the same test suite and blocks pushes/merges if tests fail.


## Model Artifacts, Feature Columns & MLflow

- Tracked runs and models are stored under `mlruns/` in this repository (for local MLflow). See the `mlruns/` folder for run artifacts and saved models.
- The serving code expects `feature_columns.json` (or `feature_columns.txt`) to align new requests with the trained model's expected inputs — those are under `artifacts/` and `src/serving/model/`.
- If using remote MLflow, set `MLFLOW_TRACKING_URI` and provide appropriate credentials in CI or your environment.


## Project structure (high-level)

- `app/` — application entrypoints (legacy or simple run scripts).
- `src/` — main source code for data, features, models, and serving:
	- `src/data/` — data loading and preprocessing.
	- `src/features/` — feature engineering.
	- `src/models/` — training, tuning, evaluation.
	- `src/serving/` — inference and model-serving utilities.
- `artifacts/` — generated artifacts like `feature_columns.json`.
- `mlruns/` — MLflow run metadata and saved models.
- `requirements.txt` — Python dependencies.
- `.github/workflows/ci.yml` — CI/CD pipeline definition.
- `tests/` — pytest test cases.


## Environment & Secrets (CI and Production)

- Docker Hub credentials (set as GitHub repo secrets) to allow CI to push images.
- Optional: MLflow remote tracking URI, cloud storage credentials for model artifacts.

Never commit secrets or credentials into the repository. Use GitHub Actions secrets or your cloud CI secret manager.


## Troubleshooting & Common Commands

- Rebuild and run locally with Docker:

```bash
docker build -t local-churn:dev .
docker run --rm -p 8000:8000 local-churn:dev
```

- Pull and run from Docker Hub:

```bash
docker pull 00pizzalover00/churn-service:latest
docker run --rm -p 8000:8000 00pizzalover00/churn-service:latest
```

- Run tests locally:

```bash
pytest -q
```


## Contributing

- Create a branch per feature or bugfix: `git checkout -b feature/your-feature`.
- Open a PR and ensure CI checks pass.
- Write tests for new functionality and update docs where necessary.


## Maintainers

- Repository owner / Docker Hub: `00pizzalover00`


## License

This project is open source. Feel free to take inspiration and create your own!
 
