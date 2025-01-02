from unittest.mock import MagicMock, patch

import numpy as np
import pandas as pd
import pytest

from src.app.model import HappyModel, SurveyMeasurement


# Test SurveyMeasurement
def test_survey_measurement_validation() -> None:
    # Valid input
    survey = SurveyMeasurement(
        city_services=4,
        housing_costs=2,
        school_quality=5,
        local_policies=3,
        maintenance=1,
        social_events=5,
    )
    assert survey.city_services == 4
    assert survey.housing_costs == 2

    # Invalid input (should raise validation error)
    with pytest.raises(ValueError):
        SurveyMeasurement(city_services=6)  # out of bounds


# Test HappyModel Initialization
@patch("pandas.read_csv")
@patch("joblib.load")
def test_happy_model_initialization_load_model(
    mock_load: MagicMock, mock_read_csv: MagicMock
) -> None:
    # Mock DataFrame returned by read_csv
    mock_df = pd.DataFrame(
        {
            "happiness": [1, 0, 1],
            "city_services": [3, 2, 4],
            "housing_costs": [3, 3, 5],
            "school_quality": [4, 2, 5],
            "local_policies": [3, 1, 4],
            "maintenance": [2, 4, 3],
            "social_events": [5, 1, 4],
        }
    )
    mock_read_csv.return_value = mock_df

    # Mock the model loading
    mock_model = MagicMock()
    mock_load.return_value = mock_model

    model = HappyModel(data_fname="happy_data.csv", model_fname="happy_model.pkl")

    # Assertions
    mock_read_csv.assert_called_once()
    mock_load.assert_called_once()
    assert model.df.equals(mock_df)
    assert model.model == mock_model


@patch("pandas.read_csv")
@patch("joblib.load")
@patch("joblib.dump")
def test_happy_model_initialization_train_model(
    mock_dump: MagicMock, mock_load: MagicMock, mock_read_csv: MagicMock
) -> None:
    # Mock DataFrame returned by read_csv
    mock_df = pd.DataFrame(
        {
            "happiness": [1, 0, 1],
            "city_services": [3, 2, 4],
            "housing_costs": [3, 3, 5],
            "school_quality": [4, 2, 5],
            "local_policies": [3, 1, 4],
            "maintenance": [2, 4, 3],
            "social_events": [5, 1, 4],
        }
    )
    mock_read_csv.return_value = mock_df

    # Simulate the model loading failure
    mock_load.side_effect = Exception("Model not found")

    model = HappyModel(data_fname="test_data.csv", model_fname="test_model.pkl")  # noqa: F841

    # Assertions
    mock_read_csv.assert_called_once()
    mock_load.assert_called_once()
    mock_dump.assert_called_once()  # Ensure model is trained and saved


# Test predict_happiness
@patch("sklearn.ensemble.GradientBoostingClassifier")
@pytest.mark.asyncio(loop_scope="session")
async def test_predict_happiness(mock_gbc: MagicMock) -> None:
    # Mock the GradientBoostingClassifier and its methods
    mock_model = mock_gbc.return_value
    mock_model.predict.return_value = [0]  # Simulate model prediction
    mock_model.predict_proba.return_value = np.array(
        [[0.2, 0.8]]
    )  # Simulate probabilities

    # Create HappyModel instance
    model = HappyModel(data_fname="happy_data.csv", model_fname="happy_model.pkl")
    model.model = mock_model  # Inject the mock model

    # Call the predict_happiness method
    prediction, probability = await model.predict_happiness(4, 3, 5, 2, 4, 1)

    # Assertions
    assert prediction == 0
    assert probability == 0.8
