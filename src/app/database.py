from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List

import duckdb

from src.app.logger import logger


@dataclass
class HappyPrediction:
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

    id: int
    city_services: int
    housing_costs: int
    school_quality: int
    local_policies: int
    maintenance: int
    social_events: int
    prediction: int
    probability: float

    class Config:
        """Config for compatibility with SQLAlchemy ORM mode."""

        orm_mode = True


def init_db(database_path: str) -> bool:
    """
    Initialize the database and ensure the required table exists.

    Args:
        database_path (str): Path to DuckDB database file.

    Returns:
        bool: True if the database was initialized successfully, False otherwise.
    """
    try:
        # Ensure the parent directory exists so DuckDB can create the file
        Path(database_path).parent.mkdir(parents=True, exist_ok=True)

        conn = duckdb.connect(database_path)
        # Create sequence first so the table's DEFAULT nextval('seq_id') can reference it
        conn.execute("CREATE SEQUENCE IF NOT EXISTS seq_id START 1")
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS happy_predictions (
                id INTEGER PRIMARY KEY DEFAULT nextval('seq_id'),
                city_services INTEGER NOT NULL,
                housing_costs INTEGER NOT NULL,
                school_quality INTEGER NOT NULL,
                local_policies INTEGER NOT NULL,
                maintenance INTEGER NOT NULL,
                social_events INTEGER NOT NULL,
                prediction INTEGER NOT NULL,
                probability FLOAT NOT NULL
            )
            """
        )
        conn.close()
        logger.info("Database initialized successfully!")
    except Exception as e:
        logger.error(f"Error initializing database: {e}")
        return False
    return True


def save_to_db(
    database_path: str, data: Dict[str, int], prediction: int, probability: float
) -> None:
    """
    Save the data into the database.

    Args:
        database_path (str): Path to DuckDB database file.
        data (Dict[str, int]): Input data containing survey measurements.
        prediction (int): The predicted happiness value.
        probability (float): The prediction probability.
    """
    try:
        # Ensure directory exists before writing
        Path(database_path).parent.mkdir(parents=True, exist_ok=True)

        conn = duckdb.connect(database_path)
        conn.execute(
            """
            INSERT INTO happy_predictions (
                city_services, housing_costs, school_quality, local_policies,
                maintenance, social_events, prediction, probability
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            [
                data["city_services"],
                data["housing_costs"],
                data["school_quality"],
                data["local_policies"],
                data["maintenance"],
                data["social_events"],
                prediction,
                probability,
            ],
        )
        conn.close()
        logger.info("Data saved to the database successfully!")
    except Exception as e:
        logger.error(f"Error saving data to the database: {e}")


def read_from_db(database_path: str) -> List[HappyPrediction]:
    """
    Read the data from the database.

    Args:
        database_path (str): Path to DuckDB database file.

    Returns:
        List[HappyPrediction]: All rows of a query result as instances of HappyPrediction.
    """
    try:
        # Ensure directory exists; if it doesn't, there are no records
        Path(database_path).parent.mkdir(parents=True, exist_ok=True)

        conn = duckdb.connect(database_path)
        result = conn.execute("SELECT * FROM happy_predictions ORDER BY id").fetchall()
        conn.close()

        # Convert result tuples to HappyPrediction objects
        records = [
            HappyPrediction(
                id=row[0],
                city_services=row[1],
                housing_costs=row[2],
                school_quality=row[3],
                local_policies=row[4],
                maintenance=row[5],
                social_events=row[6],
                prediction=row[7],
                probability=row[8],
            )
            for row in result
        ]

        logger.info("Data read from the database successfully!")
    except Exception as e:
        logger.error(f"Error reading data from database: {e}")
        return []
    return records
