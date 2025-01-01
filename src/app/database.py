import sqlite3
from pathlib import Path
from src.app.logger import logger
from typing import Dict


def init_db(DB_PATH: Path) -> bool:
    """
    Initialize the SQLite database and ensure the required table exists.

    Args:
        DB_PATH (Path): Path to the SQLite database.

    Returns:
        bool: True if the database was initialized successfully, False otherwise.
    """
    try:
        with sqlite3.connect(DB_PATH) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS happy_predictions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    city_services INTEGER,
                    housing_costs INTEGER,
                    school_quality INTEGER,
                    local_policies INTEGER,
                    maintenance INTEGER,
                    social_events INTEGER,
                    prediction INTEGER,
                    probability REAL
                )
            """)
            conn.commit()
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
        with sqlite3.connect(DB_PATH) as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT INTO happy_predictions (
                    city_services, housing_costs, school_quality, local_policies,
                    maintenance, social_events, prediction, probability
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    data["city_services"],
                    data["housing_costs"],
                    data["school_quality"],
                    data["local_policies"],
                    data["maintenance"],
                    data["social_events"],
                    prediction,
                    probability,
                ),
            )
            conn.commit()
        logger.info("Data saved to the database successfully!")
    except Exception as e:
        logger.error(f"Error saving data to the database: {e}")


def read_from_db(DB_PATH: Path) -> list:
    """
    Read the data from the SQLite database.

    Args:
        DB_PATH (Path): Path to the SQLite database.

    Returns:
        rows (list): All rows of a query result.
    """
    try:
        with sqlite3.connect(DB_PATH) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM happy_predictions")
            rows = cursor.fetchall()
        logger.info("Data read from the database successfully!")
    except Exception as e:
        logger.error(f"Error reading data from database: {e}")
        return list()
    return rows
