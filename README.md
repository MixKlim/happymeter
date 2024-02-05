# happymeter :blush:

[![Build](https://github.com/mixklim/happymeter/actions/workflows/build.yml/badge.svg)](https://github.com/mixklim/happymeter/actions/workflows/build.yml)

##### Find out how happy you are

ML model based on [Somerville Happiness Survey Data Set](https://archive.ics.uci.edu/ml/datasets/Somerville+Happiness+Survey#).

##### To run locally (from root folder):

- launch backend:
  `python -m uvicorn src.app.app:app --port=8080 --reload`
- launch front-end:
  `python -m streamlit run src\streamlit\ui.py --server.port 8501`
- unit tests: `python -m pytest`
- pre-commit: `pre-commit run --all-files`
- docker backend:
  - `docker build -t backend-image -f Dockerfile.backend .`
  - `docker run --name backend-container -p 8080:8080 --rm backend-image`
- docker frontend:
  - `docker build -t frontend-image -f Dockerfile.frontend .`
  - `docker run --name frontend-container -p 8501:8501 --rm frontend-image`
- docker compose:
  - `docker compose build`
  - `docker compose up`
