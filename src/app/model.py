from pathlib import Path

import joblib
import pandas as pd
from pydantic import BaseModel
from sklearn.ensemble import GradientBoostingClassifier


class SurveyMeasurement(BaseModel):
    """
    Class which describes a single survey measurement
    """

    city_services: int
    housing_costs: int
    school_quality: int
    local_policies: int
    maintenance: int
    social_events: int


class HappyModel:
    """
    Class for training the model and making predictions
    """

    def __init__(self) -> None:
        """
        Class constructor, loads the dataset and loads the model
        if exists. If not, calls the _train_model method and
        saves the model
        """
        self.df = pd.read_csv(Path(__file__).resolve().parent / "happy_data.csv")
        self.model_fname_ = "happy_model.pkl"
        try:
            self.model = joblib.load(Path(__file__).resolve().parent / self.model_fname_)
        except Exception:
            self.model = self._train_model()
            joblib.dump(self.model, self.model_fname_)

    def _train_model(self) -> GradientBoostingClassifier:
        """
        Perform model training using the GradientBoostingClassifier classifier
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
    ) -> tuple[str, float]:
        """
        Make a prediction based on the user-entered data
        Returns the predicted happiness with its respective probability
        """
        data_in = [[city_services, housing_costs, school_quality, local_policies, maintenance, social_events]]
        prediction = self.model.predict(data_in)
        probability = self.model.predict_proba(data_in).max()
        return prediction[0], probability
