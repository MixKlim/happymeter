# happymeter 😊

[![Build](https://github.com/mixklim/happymeter/actions/workflows/build.yml/badge.svg)](https://github.com/mixklim/happymeter/actions/workflows/build.yml)
[![Coverage Status](./reports/coverage/coverage-badge.svg?dummy=8484744)](./reports/coverage/index.html)

### Find out how happy you are
ML model based on [Somerville Happiness Survey Data Set](https://archive.ics.uci.edu/ml/datasets/Somerville+Happiness+Survey#).

### FastAPI backend
![](media/backend.png)

### Native front-end (HTML + CSS + JS)
![](media/frontend_1.png)

### Streamlit front-end
![](media/frontend_2.png)

### SQLite / PostgreSQL Database
![](media/database.png)

### Run locally (from root folder):
- Create virtual environment: `python -m venv .venv`
- Install dependencies: `poetry install --no-root`
- Launch backend: `make backend`
- Launch front-end:
  - Native: [127.0.0.1:8080](http://127.0.0.1:8080/)
  - Streamlit: `make frontend`
- Pre-commit: `make eval`
- Unit tests: `make test`
- Coverage badge: `make cov`
- End-to-end build (eval + test + cov): `make build`

### Containers:

- Populate `.env` with `POSTGRES_HOST`, `POSTGRES_USER`, `POSTGRES_PASSWORD` and `POSTGRES_DB`
- Docker backend: `make docker-backend`
- Docker frontend: `make docker-frontend`
- Docker compose: `make docker-compose`

### Deploy to Azure:

- Run `bash deploy_azure.sh`
