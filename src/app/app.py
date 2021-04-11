import uvicorn
from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pathlib import Path
from model import HappyModel, SurveyMeasurement

# Create app and model objects
app = FastAPI()

app.mount(
    "/static",
    StaticFiles(directory=Path(__file__).resolve()
    .parent.parent.absolute() / "static"),
    name="static",
)

model = HappyModel()
templates = Jinja2Templates(directory=Path(__file__).resolve()
.parent.parent.absolute() / "templates")


@app.get("/")
async def root(request: Request):
    """
    Main page for ratings
    """
    return templates.TemplateResponse(
        "index.html", context={"request": request}
        )


@app.post("/predict")
async def predict_happiness(measurement: SurveyMeasurement):
    """
    Expose the prediction functionality, make a prediction from the passed
    JSON data and return the predicted flower species with the confidence
    """
    data = measurement.dict()
    prediction, probability = await model.predict_happiness(
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
