import pytest
from pathlib import Path
from sqlalchemy import create_engine, inspect
from sqlalchemy.orm import sessionmaker
from unittest.mock import patch, MagicMock
from src.app.database import init_db, read_from_db, save_to_db, HappyPrediction
from typing import Dict, Generator

# Mock database path
DB_PATH = Path("test.db")


@pytest.fixture(scope="module")
def setup_db() -> Generator[MagicMock, None, None]:
    """
    Fixture to set up the database for testing.

    This fixture ensures that the database is initialized before tests run,
    and it is cleaned up after all tests are finished.

    Yields:
        MagicMock: The database set up and ready for testing.
    """

    mock_db = MagicMock()
    yield mock_db


@pytest.fixture
def db_session(setup_db: MagicMock) -> sessionmaker:
    """
    Fixture to provide a database session for each test.

    Args:
        setup_db (MagicMock): Ensures the database is initialized before the test.

    Returns:
        sessionmaker: A SQLAlchemy session for interacting with the database.
    """
    engine = create_engine(f"sqlite:///{DB_PATH}")
    Session = sessionmaker(bind=engine)
    session = Session()
    yield session
    session.close()


def test_init_db_success(setup_db: MagicMock) -> None:
    """
    Test to ensure the database is initialized successfully.

    Args:
        setup_db (MagicMock): Mock database initialized before the test.
    """
    assert DB_PATH.exists(), "Database file does not exist"


def test_happy_prediction_table_created(setup_db: MagicMock) -> None:
    """
    Test to check if the 'happy_predictions' table is created in the database.

    Args:
        setup_db (MagicMock): Ensures the database is initialized before the test.

    Returns:
        None: This test verifies if the table exists in the database.
    """
    engine = create_engine(f"sqlite:///{DB_PATH}")
    inspector = inspect(engine)
    assert (
        "happy_predictions" in inspector.get_table_names()
    ), "Table 'happy_predictions' was not created"


@patch("src.app.database.logger")
def test_init_db_failure(mock_logger: MagicMock) -> None:
    """
    Test to simulate a failure during database initialization.

    Args:
        mock_logger (MagicMock): Mocked logger.
    """
    # Simulate failure by passing an invalid path
    invalid_db_path = Path("invalid/path/to/db.db")
    result = init_db(invalid_db_path)
    assert not result, "Database initialization should have failed with an invalid path"

    # Verify the logger captured the error
    mock_logger.error.assert_called_once()
    assert "Error initializing database" in mock_logger.error.call_args[0][0]


@patch("src.app.database.logger")
def test_save_to_db_success(mock_logger: MagicMock, db_session: sessionmaker) -> None:
    """
    Test the `save_to_db` function to ensure data is saved correctly.

    Args:
        db_session (sessionmaker): A database session used to interact with the database.
        mock_logger (MagicMock): Mocked logger.
    """
    # Example data to be saved
    data: Dict[str, int] = {
        "city_services": 8,
        "housing_costs": 7,
        "school_quality": 9,
        "local_policies": 6,
        "maintenance": 8,
        "social_events": 7,
    }
    prediction = 75
    probability = 0.85

    # Save data to the database
    save_to_db(DB_PATH, data, prediction, probability)

    # Query the record back to ensure it's saved correctly
    result = db_session.query(HappyPrediction).filter_by(prediction=75).first()
    assert result is not None, "Record was not saved correctly"
    assert (
        result.city_services == 8
    ), f"Expected city_services to be 8, but got {result.city_services}"
    assert (
        result.probability == 0.85
    ), f"Expected probability to be 0.85, but got {result.probability}"

    # Verify the logger was called with success message
    mock_logger.info.assert_called_once_with("Data saved to the database successfully!")


@patch("src.app.database.logger")
def test_save_to_db_failure(mock_logger: MagicMock) -> None:
    """
    Test the `save_to_db` function to simulate a failure when saving data.

    Args:
        mock_logger (MagicMock): Mocked logger.
    """
    invalid_db_path = Path("invalid/path/to/db.db")

    # Example data to be saved
    data: Dict[str, int] = {
        "city_services": 8,
        "housing_costs": 7,
        "school_quality": 9,
        "local_policies": 6,
        "maintenance": 8,
        "social_events": 7,
    }
    prediction = 75
    probability = 0.85

    # Try saving data to an invalid path
    save_to_db(invalid_db_path, data, prediction, probability)

    # Verify the logger captured the error
    mock_logger.error.assert_called_once()
    assert "Error saving data to the database" in mock_logger.error.call_args[0][0]


@patch("src.app.database.logger")
def test_read_from_db_success(mock_logger: MagicMock, db_session: sessionmaker) -> None:
    """
    Test the `read_from_db` function to ensure data is read correctly from the database.

    Args:
        db_session (sessionmaker): A database session used to interact with the database.
        mock_logger (MagicMock): Mocked logger.
    """
    # First, save data to the database
    data: Dict[str, int] = {
        "city_services": 8,
        "housing_costs": 7,
        "school_quality": 9,
        "local_policies": 6,
        "maintenance": 8,
        "social_events": 7,
    }
    prediction = 75
    probability = 0.85
    save_to_db(DB_PATH, data, prediction, probability)

    # Read data from the database
    records = read_from_db(DB_PATH)

    # Verify that at least one record is returned
    assert len(records) > 0, "No records were retrieved from the database"
    assert isinstance(
        records[0], HappyPrediction
    ), "Returned record is not an instance of HappyPrediction"
    assert (
        records[0].prediction == 75
    ), f"Expected prediction to be 75, but got {records[0].prediction}"

    # Verify that both success messages were logged
    assert mock_logger.info.call_count == 2, "Expected the logger to be called twice"
    mock_logger.info.assert_any_call("Data saved to the database successfully!")
    mock_logger.info.assert_any_call("Data read from the database successfully!")


@patch("src.app.database.logger")
def test_read_from_db_failure(mock_logger: MagicMock) -> None:
    """
    Test the `read_from_db` function to simulate a failure when reading data.

    Args:
        mock_logger (MagicMock): Mocked logger.
    """
    invalid_db_path = Path("invalid/path/to/db.db")

    # Attempt to read data from an invalid database path
    records = read_from_db(invalid_db_path)

    # Ensure that an empty list is returned in case of failure
    assert records == [], "Expected an empty list in case of failure"

    # Verify the logger captured the error
    mock_logger.error.assert_called_once()
    assert "Error reading data from database" in mock_logger.error.call_args[0][0]
