from pathlib import Path

import joblib
import pandas as pd
from pydantic import BaseModel, Field
from sklearn.ensemble import GradientBoostingClassifier


class SurveyMeasurement(BaseModel):
    """
    Class which describes a single survey measurement.
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

    class Config:
        orm_mode = True  # For compatibility with SQLAlchemy ORM


class HappyModel:
    """
    Class for training the model and making predictions.
    """

    def __init__(
        self, data_fname: str = "happy_data.csv", model_fname: str = "happy_model.pkl"
    ) -> None:
        """
        Class constructor, loads the dataset and loads the model
        if exists. If not, calls the _train_model method and
        saves the model.
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
        Perform model training using the GradientBoostingClassifier classifier.
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
        Make a prediction based on the user-entered data
        Returns the predicted happiness with its respective probability.
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
