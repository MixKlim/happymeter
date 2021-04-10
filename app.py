import uvicorn
from fastapi import FastAPI
from model import HappyModel, SurveyMeasurement

# Create app and model objects
app = FastAPI()
model = HappyModel()


@app.get('/')
def root():
    """
    Root functionality
    """
    return {"name": "happiness prediction app"}


@app.post('/predict')
def predict_happiness(measurement: SurveyMeasurement):
    """
    Expose the prediction functionality, make a prediction from the passed
    JSON data and return the predicted flower species with the confidence
    """
    data = measurement.dict()
    prediction, probability = model.predict_happiness(
        data['city_services'], 
        data['housing_costs'], 
        data['school_quality'], 
        data['local_policies'],
        data['maintenance'],
        data['social_events']
    )
    return {
        'prediction': int(prediction),
        'probability': float(probability)
    }

# Run app on localhost, on port 8000
if __name__ == '__main__':
    uvicorn.run(app, host='127.0.0.1', port=8000)