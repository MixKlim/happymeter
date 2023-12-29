from pathlib import Path

import uvicorn
from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from src.app.model import HappyModel, SurveyMeasurement

# Create app and model objects
app = FastAPI()

app.mount(
    "/static",
    StaticFiles(directory=Path(__file__).resolve().parent.parent.absolute() / "static"),
    name="static",
)

model = HappyModel()
templates = Jinja2Templates(directory=Path(__file__).resolve().parent.parent.absolute() / "templates")


@app.get("/")
async def root(request: Request) -> Jinja2Templates.TemplateResponse:
    """
    Main page for ratings
    """
    return templates.TemplateResponse("index.html", context={"request": request})


@app.post("/predict")
async def predict_happiness(measurement: SurveyMeasurement) -> dict:
    """
    Expose the prediction functionality, make a prediction from the passed
    JSON data and return the prediction with the confidence
    """
    data = measurement.model_dump()
    prediction, probability = await model.predict_happiness(
        data["city_services"],
        data["housing_costs"],
        data["school_quality"],
        data["local_policies"],
        data["maintenance"],
        data["social_events"],
    )
    return {"prediction": int(prediction), "probability": float(probability)}


# Run app on localhost, on port 8080
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8080)
