import os
from pathlib import Path
from typing import List

import uvicorn
from fastapi import FastAPI, HTTPException, Request, status
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from jinja2 import Environment, FileSystemLoader

from src.app import log_config
from src.app.database import HappyPrediction, init_db, read_from_db, save_to_db
from src.app.logger import logger
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

# Templates directory setup
templates_dir = Path(__file__).resolve().parent.parent.absolute() / "templates"
templates = Jinja2Templates(directory=templates_dir)

# Jinja2 environment setup
env = Environment(loader=FileSystemLoader(templates_dir))
env.globals["url_for"] = lambda name, **path_params: app.url_path_for(
    name, **path_params
)


def get_database_url() -> str:
    """
    Check what type of database to use. Either local (SQLite) or remote (PostgreSQL).

    Returns:
        str: database url.
    """
    remote_deployment = os.getenv("REMOTE", "")
    if bool(remote_deployment):
        return f'postgresql://{os.getenv("POSTGRES_USER")}:{os.getenv("POSTGRES_PASSWORD")}@postgres/{os.getenv("POSTGRES_DB")}'
    else:
        DB_PATH = (
            Path(__file__).resolve().parent.parent.absolute()
            / "database"
            / "predictions.db"
        )
        return f"sqlite:///{DB_PATH}"


DATABASE_URL = get_database_url()
DB_INITIALIZED = init_db(DATABASE_URL)


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


logger.info("API is starting up...")


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

        if DB_INITIALIZED:
            # Save data to the database
            save_to_db(DATABASE_URL, data, prediction, probability)

        logger.info("Request handled successfully!")
        return {"prediction": prediction, "probability": probability}
    except Exception as e:
        # Unexpected error handling
        logger.error(f"Error handling request: {e}")
        raise HTTPException(status_code=500, detail="ERR_UNEXPECTED")


@app.get("/measurements", response_class=HTMLResponse)
async def read_measurements(request: Request) -> HTMLResponse:
    """
    Read all saved measurements from the SQLite database and display them in an HTML page.

    Returns:
        HTMLResponse: A response containing the HTML representation of all saved measurements.
    """
    # Read data from the database using SQLAlchemy and the HappyPrediction model
    rows: List[HappyPrediction] = read_from_db(DATABASE_URL)

    # Load the HTML template
    template = env.get_template("measurements.html")

    # Render the template with the rows
    html_content = template.render(rows=rows, request=request)
    logger.info("Measurement rows rendered successfully!")
    return HTMLResponse(content=html_content)


if __name__ == "__main__":  # pragma: no cover
    uvicorn.run(app, host="127.0.0.1", port=8000, log_config=log_config.LOGGING_CONFIG)
