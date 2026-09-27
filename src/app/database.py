import os
from typing import Any, ClassVar

from sqlalchemy import Column, Float, Integer, create_engine, event
from sqlalchemy.engine import Engine
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy.schema import CreateSchema

from src.app.logger import logger

# Define the Base class for SQLAlchemy models
Base: type[declarative_base] = declarative_base()


def _get_app_schema(app_name: str | None, client_id: str | None) -> str | None:
    if not app_name or not client_id:
        return None
    return f"{app_name}_schema_{client_id.replace('-', '')}"


APP_SCHEMA = _get_app_schema(
    os.environ.get("DATABRICKS_APP_NAME"), os.environ.get("DATABRICKS_CLIENT_ID")
)


def create_database_engine(database_url: str) -> Engine:
    engine = create_engine(database_url)
    endpoint_name = os.environ.get("ENDPOINT_NAME")
    if endpoint_name:
        from databricks.sdk import WorkspaceClient

        workspace_client = WorkspaceClient()

        @event.listens_for(engine, "do_connect")
        def add_lakebase_oauth_token(
            dialect: Any,
            connection_record: Any,
            cargs: list[Any],
            cparams: dict[str, Any],
        ) -> None:
            credential = workspace_client.postgres.generate_database_credential(
                endpoint=endpoint_name
            )
            cparams["password"] = credential.token

    return engine


class HappyPrediction(Base):
    """
    A class that represents the happy_predictions table in the database.

    Attributes:
        id (int): Primary key of the table.
        city_services (int): City services rating.
        housing_costs (int): Housing costs rating.
        school_quality (int): School quality rating.
        local_policies (int): Local policies rating.
        maintenance (int): Maintenance rating.
        social_events (int): Social events rating.
        prediction (int): Predicted happiness value.
        probability (float): Probability of the prediction.
    """

    __tablename__ = "happy_predictions"
    __table_args__: ClassVar[dict] = {"schema": APP_SCHEMA}

    id = Column(Integer, primary_key=True, autoincrement=True)
    city_services = Column(Integer, nullable=False)
    housing_costs = Column(Integer, nullable=False)
    school_quality = Column(Integer, nullable=False)
    local_policies = Column(Integer, nullable=False)
    maintenance = Column(Integer, nullable=False)
    social_events = Column(Integer, nullable=False)
    prediction = Column(Integer, nullable=False)
    probability = Column(Float, nullable=False)


def init_db(DATABASE_URL: str) -> bool:
    """
    Initialize the database and ensure the required table exists.

    Args:
        DATABASE_URL (str): Database URL.

    Returns:
        bool: True if the database was initialized successfully, False otherwise.
    """
    try:
        engine = create_database_engine(DATABASE_URL)
        if APP_SCHEMA:
            with engine.begin() as connection:
                connection.execute(CreateSchema(APP_SCHEMA, if_not_exists=True))
        Base.metadata.create_all(engine)  # Create the table if it doesn't exist
        logger.info("Database initialized successfully!")
    except SQLAlchemyError as e:
        logger.error(f"Error initializing database: {e}")
        return False
    return True


def save_to_db(
    DATABASE_URL: str, data: dict[str, int], prediction: int, probability: float
) -> None:
    """
    Save the data into the database.

    Args:
        DATABASE_URL (str): Database URL.
        data (Dict[str, int]): Input data containing survey measurements.
        prediction (int): The predicted happiness value.
        probability (float): The prediction probability.
    """
    try:
        engine = create_database_engine(DATABASE_URL)
        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
        session = SessionLocal()

        # Create an instance of HappyPrediction
        new_record = HappyPrediction(
            city_services=data["city_services"],
            housing_costs=data["housing_costs"],
            school_quality=data["school_quality"],
            local_policies=data["local_policies"],
            maintenance=data["maintenance"],
            social_events=data["social_events"],
            prediction=prediction,
            probability=probability,
        )

        # Add the new record to the session and commit the transaction
        session.add(new_record)
        session.commit()
        session.close()

        logger.info("Data saved to the database successfully!")
    except SQLAlchemyError as e:
        logger.error(f"Error saving data to the database: {e}")


def read_from_db(DATABASE_URL: str) -> list[HappyPrediction]:
    """
    Read the data from the database.

    Args:
        DATABASE_URL (str): Database URL.

    Returns:
        List[HappyPrediction]: All rows of a query result as instances of HappyPrediction.
    """
    try:
        engine = create_database_engine(DATABASE_URL)
        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
        session = SessionLocal()

        # Query the table to get all the records
        records = session.query(HappyPrediction).all()
        session.close()

        logger.info("Data read from the database successfully!")
    except SQLAlchemyError as e:
        logger.error(f"Error reading data from database: {e}")
        return []
    return records
