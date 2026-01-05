from pathlib import Path

import joblib
import pandas as pd
from pydantic import BaseModel, ConfigDict, Field
from sklearn.ensemble import GradientBoostingClassifier


class SurveyMeasurement(BaseModel):
    """
    Class which describes a single survey measurement.

    Attributes:
        city_services (int): Information about the city services (1 to 5).
        housing_costs (int): Cost of housing (1 to 5).
        school_quality (int): Overall quality of public schools (1 to 5).
        local_policies (int): Trust in the local police (1 to 5).
        maintenance (int): Maintenance of streets and sidewalks (1 to 5).
        social_events (int): Availability of social community events (1 to 5).
    """

    city_services: int = Field(
        default=3,
        title="Information about the city services",
        gt=0,
        le=5,
        description="Must be between 1 and 5",
    )
    housing_costs: int = Field(
        default=3,
        title="Cost of housing",
        gt=0,
        le=5,
        description="Must be between 1 and 5",
    )
    school_quality: int = Field(
        default=3,
        title="Overall quality of public schools",
        gt=0,
        le=5,
        description="Must be between 1 and 5",
    )
    local_policies: int = Field(
        default=3,
        title="Trust in the local police",
        gt=0,
        le=5,
        description="Must be between 1 and 5",
    )
    maintenance: int = Field(
        default=3,
        title="Maintenance of streets and sidewalks",
        gt=0,
        le=5,
        description="Must be between 1 and 5",
    )
    social_events: int = Field(
        default=3,
        title="Availability of social community events",
        gt=0,
        le=5,
        description="Must be between 1 and 5",
    )


class HappyPrediction(SurveyMeasurement):
    """
    A class representing a prediction based on survey measurements.

    Attributes:
        prediction (int): Predicted happiness value.
        probability (float): Probability of the prediction.
    """

    prediction: int
    probability: float

    model_config = ConfigDict(from_attributes=True)


class HappyModel:
    """
    Class for training the model and making predictions.

    Attributes:
        df_fname_ (str): The filename of the dataset.
        df (DataFrame): The loaded dataset.
        model_fname_ (str): The filename of the model.
        model (GradientBoostingClassifier): The trained machine learning model.
    """

    def __init__(
        self, data_fname: str = "happy_data.csv", model_fname: str = "happy_model.pkl"
    ) -> None:
        """
        Class constructor, loads the dataset and the model if it exists.
        If the model does not exist, it trains a new model and saves it.

        Args:
            data_fname (str): The filename of the dataset.
            model_fname (str): The filename of the model.
        """
        self.df_fname_ = data_fname
        self.df = pd.read_csv(
            Path(__file__).resolve().parent.parent.absolute() / "data" / self.df_fname_
        )
        self.model_fname_ = model_fname
        try:
            self.model = joblib.load(
                Path(__file__).resolve().parent.parent.absolute()
                / "model"
                / self.model_fname_
            )
        except Exception:
            self.model = self._train_model()
            joblib.dump(
                self.model,
                Path(__file__).resolve().parent.parent.absolute()
                / "model"
                / self.model_fname_,
            )

    def _train_model(self) -> GradientBoostingClassifier:
        """
        Train a GradientBoostingClassifier model using the dataset.

        Returns:
            GradientBoostingClassifier: The trained model.
        """
        X = self.df.drop("happiness", axis=1)
        y = self.df["happiness"]
        gfc = GradientBoostingClassifier(
            n_estimators=10,
            learning_rate=0.1,
            max_depth=3,
            max_features="sqrt",
            loss="log_loss",
            criterion="friedman_mse",
            subsample=1.0,
            random_state=42,
        )
        model = gfc.fit(X.values, y.values)
        return model

    async def predict_happiness(
        self,
        city_services: int,
        housing_costs: int,
        school_quality: int,
        local_policies: int,
        maintenance: int,
        social_events: int,
    ) -> tuple[int, float]:
        """
        Make a prediction based on the user-entered data.
        Returns the predicted happiness with its respective probability.

        Args:
            city_services (int): Rating for city services.
            housing_costs (int): Rating for housing costs.
            school_quality (int): Rating for school quality.
            local_policies (int): Rating for trust in local policies.
            maintenance (int): Rating for maintenance of infrastructure.
            social_events (int): Rating for availability of social events.

        Returns:
            tuple[int, float]: The prediction (happiness value) and the associated probability.
        """
        data_in = [
            [
                city_services,
                housing_costs,
                school_quality,
                local_policies,
                maintenance,
                social_events,
            ]
        ]

        prediction = self.model.predict(data_in)
        probability = self.model.predict_proba(data_in).max()
        return int(prediction[0]), float(probability)
