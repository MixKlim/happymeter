from pathlib import Path

import uvicorn
from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from src.app.model import HappyModel, SurveyMeasurement

# Create app and model objects
app = FastAPI(
    title="Happiness Prediction",
    version="1.0",
    description="Find out how happy you are",
)

app.mount(
    "/static",
    StaticFiles(directory=Path(__file__).resolve().parent.parent.absolute() / "static"),
    name="static",
)

model = HappyModel()
templates = Jinja2Templates(
    directory=Path(__file__).resolve().parent.parent.absolute() / "templates"
)


@app.get("/")
async def root(request: Request) -> None:
    """
    Main page for ratings
    """
    return templates.TemplateResponse(request=request, name="index.html")


@app.post("/predict")
async def predict_happiness(measurement: SurveyMeasurement) -> dict:
    """
    Expose the prediction functionality, make a prediction from the passed
    JSON data and return the prediction with the confidence
    """
    data = measurement.dict()
    prediction, probability = await model.predict_happiness(
        data["city_services"],
        data["housing_costs"],
        data["school_quality"],
        data["local_policies"],
        data["maintenance"],
        data["social_events"],
    )
    return {"prediction": int(prediction), "probability": float(probability)}


if __name__ == "__main__":  # pragma: no cover
    uvicorn.run(app, host="127.0.0.1", port=8000)
