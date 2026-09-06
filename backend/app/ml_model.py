from __future__ import annotations

from datetime import date

import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, r2_score

from .data_loader import EnvironmentRecord


class EnvironmentalForecaster:
    """Small, explainable baseline model for the next month's indicators."""

    def __init__(self, records: tuple[EnvironmentRecord, ...]) -> None:
        if len(records) < 4:
            raise ValueError("At least four monthly records are required to train the model")
        self.records = records
        self.model = RandomForestRegressor(n_estimators=100, random_state=42)
        self.validation = self._validate()
        self._train()

    @staticmethod
    def _features(record: EnvironmentRecord) -> list[float]:
        return [record.observed_month.month, record.rainfall_mm, record.ndvi, record.water_percent]

    def _train(self) -> None:
        inputs = np.array([self._features(record) for record in self.records[:-1]])
        targets = np.array([[record.rainfall_mm, record.ndvi, record.water_percent] for record in self.records[1:]])
        self.model.fit(inputs, targets)

    def _validate(self) -> dict[str, object]:
        """Test the model on the latest records, never on the training records."""
        transitions = len(self.records) - 1
        test_count = max(2, round(transitions * 0.2))
        train_end = transitions - test_count
        train_records = self.records[: train_end + 1]
        test_inputs = np.array([self._features(record) for record in self.records[train_end:-1]])
        test_targets = np.array([[record.rainfall_mm, record.ndvi, record.water_percent] for record in self.records[train_end + 1 :]])
        validation_model = RandomForestRegressor(n_estimators=100, random_state=42)
        train_inputs = np.array([self._features(record) for record in train_records[:-1]])
        train_targets = np.array([[record.rainfall_mm, record.ndvi, record.water_percent] for record in train_records[1:]])
        validation_model.fit(train_inputs, train_targets)
        predictions = validation_model.predict(test_inputs)

        metric_names = ("rainfall_mm", "ndvi", "water_percent")
        metrics = {}
        for index, name in enumerate(metric_names):
            errors = test_targets[:, index] - predictions[:, index]
            metrics[name] = {
                "mae": round(float(mean_absolute_error(test_targets[:, index], predictions[:, index])), 4),
                "rmse": round(float(np.sqrt(np.mean(errors**2))), 4),
                "r2": round(float(r2_score(test_targets[:, index], predictions[:, index])), 4),
            }
        return {
            "train_records": len(train_records),
            "test_records": test_count,
            "test_period": {
                "from": self.records[train_end + 1].observed_month.strftime("%Y-%m"),
                "to": self.records[-1].observed_month.strftime("%Y-%m"),
            },
            "metrics": metrics,
        }

    def predict(self, month: date) -> dict[str, float | str]:
        latest = self.records[-1]
        prediction = self.model.predict([self._features(EnvironmentRecord(month, latest.rainfall_mm, latest.ndvi, latest.water_percent))])[0]
        return {
            "month": month.strftime("%Y-%m"),
            "rainfall_mm": round(float(max(prediction[0], 0)), 1),
            "ndvi": round(float(np.clip(prediction[1], -1, 1)), 3),
            "water_percent": round(float(np.clip(prediction[2], 0, 100)), 2),
            "model": "RandomForestRegressor baseline",
        }