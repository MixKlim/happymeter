import sqlite3
from pathlib import Path
import pytest
from unittest.mock import patch, MagicMock
from typing import Generator

from src.app.database import init_db, read_from_db, save_to_db


@pytest.fixture
def temp_db_path(
    tmp_path: Path, request: pytest.FixtureRequest
) -> Generator[Path, None, None]:
    """Fixture to create a temporary SQLite database file, optionally with a predefined table.

    Args:
        tmp_path (Path): Pytest-provided temporary path.
        request (FixtureRequest): Pytest request object for parameterizing the fixture.

    Yields:
        Path: Path to the temporary SQLite database file.
    """
    db_path = tmp_path / "test.db"

    # Check if the test requests a pre-initialized table
    with sqlite3.connect(db_path) as conn:
        if getattr(request, "param", False):  # `True` if a table is requested
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

    yield db_path


# Test cases
@patch("src.app.database.logger")
def test_init_db_success(mock_logger: MagicMock, temp_db_path: Path) -> None:
    """Test that the init_db function creates the required table and logs success.

    Args:
        mock_logger (MagicMock): Mocked logger.
        temp_db_path (Path): Path to a temporary SQLite database file.
    """
    # Call the function to initialize the database
    result = init_db(temp_db_path)

    # Assert the function returned True
    assert result is True

    # Verify the table was created
    with sqlite3.connect(temp_db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT name
            FROM sqlite_master
            WHERE type='table' AND name='happy_predictions';
        """)
        table = cursor.fetchone()
        assert table is not None, "Table 'happy_predictions' was not created"

    # Verify the logger was called with success message
    mock_logger.info.assert_called_once_with("Database initialized successfully!")


@patch("src.app.database.logger")
def test_init_db_failure(mock_logger: MagicMock, temp_db_path: Path) -> None:
    """Test that init_db logs an error and returns False when an exception occurs.

    Args:
        mock_logger (MagicMock): Mocked logger.
        temp_db_path (Path): Path to a temporary SQLite database file.
    """
    # Induce an error by passing a non-writable path
    non_writable_path = Path("/invalid_path/test.db")

    # Call the function and assert it returns False
    result = init_db(non_writable_path)
    assert result is False

    # Verify the logger captured the error
    mock_logger.error.assert_called_once()
    assert "Error initializing database" in mock_logger.error.call_args[0][0]


@pytest.mark.parametrize("temp_db_path", [True], indirect=True)
@patch("src.app.database.logger")
def test_save_to_db_success(mock_logger: MagicMock, temp_db_path: Path) -> None:
    """Test that save_to_db inserts data into the database and logs success.

    Args:
        mock_logger (MagicMock): Mocked logger.
        temp_db_path (Path): Path to a temporary SQLite database file with the required table.
    """
    data = {
        "city_services": 5,
        "housing_costs": 7,
        "school_quality": 8,
        "local_policies": 6,
        "maintenance": 9,
        "social_events": 4,
    }
    prediction = 85
    probability = 0.92

    # Call the function to save data
    save_to_db(temp_db_path, data, prediction, probability)

    # Verify the data was inserted
    with sqlite3.connect(temp_db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM happy_predictions")
        rows = cursor.fetchall()
        assert len(rows) == 1, "Data was not inserted into the database"
        inserted_row = rows[0]
        assert inserted_row[1:7] == tuple(data.values()), "Inserted data does not match"
        assert inserted_row[7] == prediction, "Prediction value does not match"
        assert inserted_row[8] == probability, "Probability value does not match"

    # Verify the logger was called with success message
    mock_logger.info.assert_called_once_with("Data saved to the database successfully!")


@pytest.mark.parametrize("temp_db_path", [True], indirect=True)
@patch("src.app.database.logger")
def test_save_to_db_failure(mock_logger: MagicMock, temp_db_path: Path) -> None:
    """Test that save_to_db logs an error when an exception occurs.

    Args:
        mock_logger (MagicMock): Mocked logger.
        temp_db_path (Path): Path to a temporary SQLite database file with the required table.
    """
    # Induce an error by omitting a required column in the data
    invalid_data = {
        "city_services": 5,
        "housing_costs": 7,
        # "school_quality" missing
        "local_policies": 6,
        "maintenance": 9,
        "social_events": 4,
    }
    prediction = 85
    probability = 0.92

    # Call the function and expect it to handle the exception
    save_to_db(temp_db_path, invalid_data, prediction, probability)

    # Verify the logger captured the error
    mock_logger.error.assert_called_once()
    assert "Error saving data to the database" in mock_logger.error.call_args[0][0]


@pytest.mark.parametrize("temp_db_path", [True], indirect=True)
@patch("src.app.database.logger")
def test_read_from_db_success(mock_logger: MagicMock, temp_db_path: Path) -> None:
    """Test that read_from_db returns data correctly and logs success.

    Args:
        mock_logger (MagicMock): Mocked logger.
        temp_db_path (Path): Path to a temporary SQLite database file with the required table and data.
    """
    # Prepopulate the database with some data
    test_data = [
        (1, 5, 7, 8, 6, 9, 4, 85, 0.92),
        (2, 4, 6, 7, 5, 8, 3, 80, 0.85),
    ]
    with sqlite3.connect(temp_db_path) as conn:
        cursor = conn.cursor()
        cursor.executemany(
            """
            INSERT INTO happy_predictions (
                id, city_services, housing_costs, school_quality, local_policies,
                maintenance, social_events, prediction, probability
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
            test_data,
        )
        conn.commit()

    # Call the function
    result = read_from_db(temp_db_path)

    # Verify the function returns the correct data
    assert result == test_data, "The returned data does not match the expected data"

    # Verify the logger logs a success message
    mock_logger.info.assert_called_once_with(
        "Data read from the database successfully!"
    )


@patch("src.app.database.logger")
def test_read_from_db_failure(mock_logger: MagicMock, temp_db_path: Path) -> None:
    """Test that read_from_db logs an error and returns an empty list when an exception occurs.

    Args:
        mock_logger (MagicMock): Mocked logger.
        temp_db_path (Path): Path to a temporary SQLite database file.
    """
    # Induce an error by not creating the required table
    # Call the function and expect it to handle the exception gracefully
    result = read_from_db(temp_db_path)

    # Verify the function returns an empty list
    assert result == [], "The function did not return an empty list on failure"

    # Verify the logger captured the error
    mock_logger.error.assert_called_once()
    assert "Error reading data from database" in mock_logger.error.call_args[0][0]
