# happymeter :blush:

[![Build](https://github.com/mixklim/happymeter/actions/workflows/build.yml/badge.svg)](https://github.com/mixklim/happymeter/actions/workflows/build.yml)
[![Coverage Status](./reports/coverage/coverage-badge.svg?dummy=8484744)](./reports/coverage/index.html)

##### Find out how happy you are

ML model based on [Somerville Happiness Survey Data Set](https://archive.ics.uci.edu/ml/datasets/Somerville+Happiness+Survey#).

##### To run locally (from root folder):

- create virtual environment: `python -m venv .venv`
- install dependencies: `poetry install --no-root`
- launch backend:
  `make backend`
- launch front-end:
  - native (HTML + CSS + JS): [127.0.0.1:8080](http://127.0.0.1:8080/)
  - streamlit: `make frontend`
- pre-commit: `make eval`
- unit tests: `make test`
- coverage badge: `make cov`
- end-to-end build (eval + test + cov): `make build`

##### Containers:

- docker backend: `make docker-backend`
- docker frontend: `make docker-frontend`
- docker compose: `make docker-compose`
