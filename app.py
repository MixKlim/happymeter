import uvicorn
from fastapi import FastAPI
from model import IrisModel, IrisSpecies

# Create app and model objects
app = FastAPI()
model = IrisModel()


# Root functionality
@app.get('/')
def root():
    return {"name": "iris flower prediction app"}


# Expose the prediction functionality, make a prediction from the passed
# JSON data and return the predicted flower species with the confidence
@app.post('/predict')
def predict_species(iris: IrisSpecies):
    data = iris.dict()
    prediction, probability = model.predict_species(
        data['sepal_length'], data['sepal_width'], data['petal_length'], data['petal_width']
    )
    return {
        'prediction': prediction,
        'probability': probability
    }

# Run app on localhost, on port 8000
if __name__ == '__main__':
    uvicorn.run(app, host='127.0.0.1', port=8000)