# happymeter

Find out how happy you are <br>
Based on [Somerville Happiness Survey Data Set](https://archive.ics.uci.edu/ml/datasets/Somerville+Happiness+Survey#)

### To run locally (from root folder):

- launch fastapi: `python -m uvicorn src.app.app:app --port=8080 --reload`
- launch streamlit: `python -m streamlit run src\streamlit\ui.py --server.port 8088`
- unit tests: `python -m pytest`
- pre-commit: `pre-commit run --all-files`
