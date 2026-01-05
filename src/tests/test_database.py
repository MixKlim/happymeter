from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from src.app.database import HappyPrediction, init_db, read_from_db, save_to_db


@pytest.fixture
def mock_database_path(tmp_path: Path) -> str:
    """
    Fixture to provide a mock database path for testing using an in-memory DuckDB.

    Args:
        tmp_path: pytest's temporary directory fixture.

    Returns:
        str: Path to a temporary DuckDB database file.
    """
    return str(tmp_path / "test_predictions.duckdb")


# Test cases
@patch("src.app.database.logger")
def test_init_db_success(mock_logger: MagicMock, mock_database_path: str) -> None:
    """
    Test `init_db` for successful database initialization.

    Args:
        mock_logger: Mock for logging.
        mock_database_path (str): Mock database path.
    """
    result = init_db(mock_database_path)

    assert result is True

    # Verify the logger was called with success message
    mock_logger.info.assert_called_once_with("Database initialized successfully!")


@patch("src.app.database.logger")
def test_init_db_failure(mock_logger: MagicMock) -> None:
    """
    Test `init_db` for failure during database initialization.

    Args:
        mock_logger: Mock for logging.
    """
    # Use an invalid path that cannot be created
    invalid_path = "/invalid/path/that/does/not/exist/predictions.duckdb"

    result = init_db(invalid_path)

    assert result is False

    # Verify the logger captured the error
    mock_logger.error.assert_called_once()
    assert "Error initializing database" in mock_logger.error.call_args[0][0]


@patch("src.app.database.logger")
def test_save_to_db_success(mock_logger: MagicMock, mock_database_path: str) -> None:
    """
    Test `save_to_db` for successful data saving.

    Args:
        mock_logger: Mock for logging.
        mock_database_path (str): Mock database path.
    """
    # Initialize database
    init_db(mock_database_path)

    # Test data
    data = {
        "city_services": 8,
        "housing_costs": 6,
        "school_quality": 7,
        "local_policies": 5,
        "maintenance": 9,
        "social_events": 4,
    }

    # Call save_to_db
    save_to_db(mock_database_path, data, prediction=1, probability=0.85)

    # Verify data was saved by reading it back
    records = read_from_db(mock_database_path)
    assert len(records) > 0, "No records were saved to the database"
    assert records[0].city_services == 8
    import pytest

    assert records[0].probability == pytest.approx(0.85, rel=1e-6)

    # Verify logger info message (may be called multiple times; ensure the save message was logged)
    mock_logger.info.assert_any_call("Data saved to the database successfully!")


@patch("src.app.database.logger")
def test_save_to_db_failure(mock_logger: MagicMock) -> None:
    """
    Test the `save_to_db` function to simulate a failure when saving data.

    Args:
        mock_logger: Mocked logger.
    """
    invalid_db_path = "/invalid/path/predictions.duckdb"

    # Example data to be saved
    data = {
        "city_services": 8,
        "housing_costs": 6,
        "school_quality": 7,
        "local_policies": 5,
        "maintenance": 9,
        "social_events": 4,
    }

    # Try saving data to an invalid path
    save_to_db(invalid_db_path, data, prediction=75, probability=0.85)

    # Verify the logger captured the error
    mock_logger.error.assert_called_once()
    assert "Error saving data to the database" in mock_logger.error.call_args[0][0]


@patch("src.app.database.logger")
def test_read_from_db_success(mock_logger: MagicMock, mock_database_path: str) -> None:
    """
    Test `read_from_db` for successful data retrieval.

    Args:
        mock_logger: Mock for logging.
        mock_database_path (str): Mock database path.
    """
    # Initialize database
    init_db(mock_database_path)

    # Add test data
    test_data = {
        "city_services": 8,
        "housing_costs": 6,
        "school_quality": 7,
        "local_policies": 5,
        "maintenance": 9,
        "social_events": 4,
    }
    save_to_db(mock_database_path, test_data, prediction=1, probability=0.95)

    # Act
    records = read_from_db(mock_database_path)

    # Assert
    assert len(records) > 0, "No records were retrieved from the database"
    assert isinstance(records[0], HappyPrediction), (
        "Returned record is not an instance of HappyPrediction"
    )
    assert records[0].prediction == 1, (
        f"Expected prediction to be 1, but got {records[0].prediction}"
    )
    assert records[0].city_services == 8

    # Verify the logger was called with success message
    assert any(
        "Data read from the database successfully!" in str(call)
        for call in mock_logger.info.call_args_list
    )


@patch("src.app.database.logger")
def test_read_from_db_failure(mock_logger: MagicMock) -> None:
    """
    Test the `read_from_db` function to simulate a failure when reading data.

    Args:
        mock_logger: Mocked logger.
    """
    invalid_db_path = "/invalid/path/predictions.duckdb"

    # Attempt to read data from an invalid database path
    records = read_from_db(invalid_db_path)

    # Ensure that an empty list is returned in case of failure
    assert records == [], "Expected an empty list in case of failure"

    # Verify the logger captured the error
    mock_logger.error.assert_called_once()
    assert "Error reading data from database" in mock_logger.error.call_args[0][0]
