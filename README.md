# happymeter 😊

[![Build](https://github.com/mixklim/happymeter/actions/workflows/build.yml/badge.svg)](https://github.com/mixklim/happymeter/actions/workflows/build.yml)
[![Coverage Status](https://raw.githubusercontent.com/mixklim/happymeter/main/reports/coverage/coverage-badge.svg?dummy=8484744)](https://raw.githubusercontent.com/mixklim/happymeter/main/reports/coverage/index.html)

### Find out how happy you are

ML model based on [Somerville Happiness Survey Data Set](https://archive.ics.uci.edu/ml/datasets/Somerville+Happiness+Survey#).

### FastAPI backend

![](https://raw.githubusercontent.com/mixklim/happymeter/main/media/backend.png)

### Native front-end (HTML + CSS + JS)

![](https://raw.githubusercontent.com/mixklim/happymeter/main/media/frontend_1.png)

### Streamlit front-end

![](https://raw.githubusercontent.com/mixklim/happymeter/main/media/frontend_2.png)

### SQLite / PostgreSQL Database

![](https://raw.githubusercontent.com/mixklim/happymeter/main/media/database.png)

### Run locally (from root folder):

- Create virtual environment: `uv venv --python 3.12`
- Install dependencies: `uv sync --all-groups`
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

### Deploy to Azure (Container Apps):

- Run `bash deploy_azure.sh`
