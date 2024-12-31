from pathlib import Path

import uvicorn
from fastapi import FastAPI, HTTPException, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from src.app.model import HappyModel, SurveyMeasurement
from src.app import log_config
from src.app.logger import logger

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


# Reuse FastAPI's exception handlers
@app.exception_handler(RequestValidationError)
async def standard_validation_exception_handler(
    request: Request, exc: RequestValidationError
) -> JSONResponse:
    # Log the validation error details
    logger.error(f"422 Validation Error: {exc.errors()} | Request Body: {exc.body}")

    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content=jsonable_encoder({"detail": exc.errors(), "body": exc.body}),
    )


logger.info("API is starting up")


@app.get("/")
async def root(request: Request) -> None:
    """
    Main page for ratings.
    """
    return templates.TemplateResponse(request=request, name="index.html")


@app.post("/predict")
async def predict_happiness(measurement: SurveyMeasurement) -> dict:
    """
    Expose the prediction functionality, make a prediction from the passed
    JSON data and return the prediction with the confidence.
    """
    try:
        data = measurement.dict()
        prediction, probability = await model.predict_happiness(
            data["city_services"],
            data["housing_costs"],
            data["school_quality"],
            data["local_policies"],
            data["maintenance"],
            data["social_events"],
        )
        logger.info("Request handled successfully!")
        return {"prediction": int(prediction), "probability": float(probability)}
    except Exception as e:
        # Unexpected error handling
        logger.error(f"Error handling request: {e}")
        raise HTTPException(status_code=500, detail="ERR_UNEXPECTED")


if __name__ == "__main__":  # pragma: no cover
    uvicorn.run(app, host="127.0.0.1", port=8000, log_config=log_config.LOGGING_CONFIG)
