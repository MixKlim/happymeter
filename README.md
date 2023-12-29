# happymeter

Find out how happy you are <br>
Based on [Somerville Happiness Survey Data Set](https://archive.ics.uci.edu/ml/datasets/Somerville+Happiness+Survey#)

### To run locally (from root folder):

- launch: `python -m uvicorn src.app.app:app --port=8080 --reload`
- test: `python -m pytest`
- pre-commit: `pre-commit run --all-files`
