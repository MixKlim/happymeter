from unittest.mock import MagicMock, patch

import pytest
from sqlalchemy.exc import OperationalError

from src.app.database import HappyPrediction, init_db, read_from_db, save_to_db


@pytest.fixture
def mock_database_url() -> str:
    """
    Fixture to provide a mock database URL for testing.

    Returns:
        str: A mock SQLite in-memory database URL.
    """
    return "sqlite:///:memory:"


# Test cases
@patch("src.app.database.logger")
@patch("src.app.database.Base.metadata.create_all")
@patch("src.app.database.create_engine")
def test_init_db_success(
    mock_create_engine: MagicMock,
    mock_create_all: MagicMock,
    mock_logger: MagicMock,
    mock_database_url: str,
) -> None:
    """
    Test `init_db` for successful database initialization.

    Args:
        mock_create_engine (MagicMock): Mock for SQLAlchemy's `create_engine`.
        mock_create_all (MagicMock): Mock for SQLAlchemy's metadata `create_all`.
        mock_logger (MagicMock): Mock for logging.
        mock_database_url (str): Mock database URL.
    """
    mock_engine = MagicMock()
    mock_create_engine.return_value = mock_engine

    result = init_db(mock_database_url)

    assert result is True
    mock_create_engine.assert_called_once_with(mock_database_url)
    mock_create_all.assert_called_once_with(mock_engine)

    # Verify the logger was called with success message
    mock_logger.info.assert_called_once_with("Database initialized successfully!")


@patch("src.app.database.logger")
@patch("src.app.database.create_engine")
def test_init_db_failure(
    mock_create_engine: MagicMock, mock_logger: MagicMock, mock_database_url: str
) -> None:
    """
    Test `init_db` for failure during database initialization.

    Args:
        mock_create_engine (MagicMock): Mock for SQLAlchemy's `create_engine`.
        mock_logger (MagicMock): Mock for logging.
        mock_database_url (str): Mock database URL.
    """
    mock_create_engine.side_effect = OperationalError("error", {}, None)

    result = init_db(mock_database_url)

    assert result is False
    mock_create_engine.assert_called_once_with(mock_database_url)

    # Verify the logger captured the error
    mock_logger.error.assert_called_once()
    assert "Error initializing database" in mock_logger.error.call_args[0][0]


@patch("src.app.database.Base.metadata.create_all")
@patch("src.app.database.create_engine")
def test_init_db_metadata_error(
    mock_create_engine: MagicMock, mock_create_all: MagicMock, mock_database_url: str
) -> None:
    """
    Test `init_db` for failure due to metadata creation error.

    Args:
        mock_create_engine (MagicMock): Mock for SQLAlchemy's `create_engine`.
        mock_create_all (MagicMock): Mock for SQLAlchemy's metadata `create_all`.
        mock_database_url (str): Mock database URL.
    """
    mock_engine = MagicMock()
    mock_create_engine.return_value = mock_engine
    mock_create_all.side_effect = Exception("Metadata error")

    result = init_db(mock_database_url)

    assert result is False
    mock_create_engine.assert_called_once_with(mock_database_url)
    mock_create_all.assert_called_once_with(mock_engine)


@patch("src.app.database.logger")
@patch("src.app.database.sessionmaker")
@patch("src.app.database.create_engine")
def test_save_to_db_success(
    mock_create_engine: MagicMock,
    mock_sessionmaker: MagicMock,
    mock_logger: MagicMock,
    mock_database_url: str,
) -> None:
    """
    Test `save_to_db` for successful data saving.

    Args:
        mock_create_engine (MagicMock): Mock for SQLAlchemy's `create_engine`.
        mock_sessionmaker (MagicMock): Mock for SQLAlchemy's `sessionmaker`.
        mock_logger (MagicMock): Mock for logging.
        mock_database_url (str): Mock database URL.
    """
    # Mock engine and session setup
    mock_engine = MagicMock()
    mock_session = MagicMock()
    mock_create_engine.return_value = mock_engine
    mock_sessionmaker.return_value = lambda **kwargs: mock_session

    # Mock the query chain for session
    mock_query = MagicMock()
    mock_filter_by = MagicMock()
    mock_query.filter_by.return_value = mock_filter_by
    mock_filter_by.first.return_value = HappyPrediction(
        city_services=8,
        housing_costs=6,
        school_quality=7,
        local_policies=5,
        maintenance=9,
        social_events=4,
        prediction=1,
        probability=0.85,
    )
    mock_session.query.return_value = mock_query

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
    save_to_db(mock_database_url, data, prediction=1, probability=0.85)

    # Assert session methods are called correctly
    mock_session.add.assert_called_once()
    mock_session.commit.assert_called_once()
    mock_session.close.assert_called_once()

    # Assert that the data is saved correctly
    result = mock_session.query(HappyPrediction).filter_by(prediction=1).first()
    assert result is not None, "Record was not saved correctly"
    assert result.city_services == 8, (
        f"Expected city_services to be 8, but got {result.city_services}"
    )
    assert result.probability == 0.85, (
        f"Expected probability to be 0.85, but got {result.probability}"
    )

    # Verify logger info message
    mock_logger.info.assert_called_once_with("Data saved to the database successfully!")


@patch("src.app.database.logger")
def test_save_to_db_failure(mock_logger: MagicMock) -> None:
    """
    Test the `save_to_db` function to simulate a failure when saving data.

    Args:
        mock_logger (MagicMock): Mocked logger.
    """
    invalid_db_url = ""

    # Example data to be saved
    data = {
        "city_services": 8,
        "housing_costs": 6,
        "school_quality": 7,
        "local_policies": 5,
        "maintenance": 9,
        "social_events": 4,
    }

    # Try saving data to an invalid URL
    save_to_db(invalid_db_url, data, prediction=75, probability=0.85)

    # Verify the logger captured the error
    mock_logger.error.assert_called_once()
    assert "Error saving data to the database" in mock_logger.error.call_args[0][0]


@patch("src.app.database.logger")
@patch("src.app.database.create_engine")
@patch("src.app.database.sessionmaker")
def test_read_from_db_success(
    mock_sessionmaker: MagicMock,
    mock_create_engine: MagicMock,
    mock_logger: MagicMock,
    mock_database_url: str,
) -> None:
    """
    Test `read_from_db` for successful data retrieval.

    Args:
        mock_sessionmaker (MagicMock): Mock for SQLAlchemy's `sessionmaker`.
        mock_create_engine (MagicMock): Mock for SQLAlchemy's `create_engine`.
        mock_logger (MagicMock): Mock for logging.
        mock_database_url (str): Mock database URL.
    """
    # Create mock objects for the engine and session
    mock_engine = MagicMock()
    mock_session = MagicMock()
    mock_create_engine.return_value = mock_engine
    mock_sessionmaker.return_value = lambda: mock_session

    # Prepare the mock query and its return value
    mock_query = MagicMock()
    mock_session.query.return_value = mock_query

    expected_records = [
        HappyPrediction(
            city_services=8,
            housing_costs=6,
            school_quality=7,
            local_policies=5,
            maintenance=9,
            social_events=4,
            prediction=1,
            probability=0.95,
        )
    ]
    mock_query.all.return_value = expected_records

    # Act
    records = read_from_db(mock_database_url)

    # Assert
    assert records == expected_records
    mock_session.close.assert_called_once()

    # Verify that at least one record is returned
    assert len(records) > 0, "No records were retrieved from the database"
    assert isinstance(records[0], HappyPrediction), (
        "Returned record is not an instance of HappyPrediction"
    )
    assert records[0].prediction == 1, (
        f"Expected prediction to be 1, but got {records[0].prediction}"
    )

    ## Verify the logger was called with success message
    mock_logger.info.assert_any_call("Data read from the database successfully!")


@patch("src.app.database.logger")
def test_read_from_db_failure(mock_logger: MagicMock) -> None:
    """
    Test the `read_from_db` function to simulate a failure when reading data.

    Args:
        mock_logger (MagicMock): Mocked logger.
    """
    invalid_db_url = ""

    # Attempt to read data from an invalid database URL
    records = read_from_db(invalid_db_url)

    # Ensure that an empty list is returned in case of failure
    assert records == [], "Expected an empty list in case of failure"

    # Verify the logger captured the error
    mock_logger.error.assert_called_once()
    assert "Error reading data from database" in mock_logger.error.call_args[0][0]
