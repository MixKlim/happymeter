from pathlib import Path
from typing import Dict, List, Type
from sqlalchemy import create_engine, Column, Integer, Float
from sqlalchemy.orm import sessionmaker, declarative_base
from src.app.logger import logger

# Define the Base class for SQLAlchemy models
Base: Type[declarative_base] = declarative_base()


class HappyPrediction(Base):
    """
    A class that represents the happy_predictions table in the SQLite database.

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

    id = Column(Integer, primary_key=True, autoincrement=True)
    city_services = Column(Integer, nullable=False)
    housing_costs = Column(Integer, nullable=False)
    school_quality = Column(Integer, nullable=False)
    local_policies = Column(Integer, nullable=False)
    maintenance = Column(Integer, nullable=False)
    social_events = Column(Integer, nullable=False)
    prediction = Column(Integer, nullable=False)
    probability = Column(Float, nullable=False)


def init_db(DB_PATH: Path) -> bool:
    """
    Initialize the SQLite database and ensure the required table exists.

    Args:
        DB_PATH (Path): Path to the SQLite database.

    Returns:
        bool: True if the database was initialized successfully, False otherwise.
    """
    try:
        engine = create_engine(f"sqlite:///{DB_PATH}")
        Base.metadata.create_all(engine)  # Create the table if it doesn't exist
        logger.info("Database initialized successfully!")
    except Exception as e:
        logger.error(f"Error initializing database: {e}")
        return False
    return True


def save_to_db(
    DB_PATH: Path, data: Dict[str, int], prediction: int, probability: float
) -> None:
    """
    Save the data into the SQLite database.

    Args:
        DB_PATH (Path): Path to the SQLite database.
        data (Dict[str, int]): Input data containing survey measurements.
        prediction (int): The predicted happiness value.
        probability (float): The prediction probability.
    """
    try:
        engine = create_engine(f"sqlite:///{DB_PATH}")
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
    except Exception as e:
        logger.error(f"Error saving data to the database: {e}")


def read_from_db(DB_PATH: Path) -> List[HappyPrediction]:
    """
    Read the data from the SQLite database.

    Args:
        DB_PATH (Path): Path to the SQLite database.

    Returns:
        List[HappyPrediction]: All rows of a query result as instances of HappyPrediction.
    """
    try:
        engine = create_engine(f"sqlite:///{DB_PATH}")
        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
        session = SessionLocal()

        # Query the table to get all the records
        records = session.query(HappyPrediction).all()
        session.close()

        logger.info("Data read from the database successfully!")
    except Exception as e:
        logger.error(f"Error reading data from database: {e}")
        return []
    return records
