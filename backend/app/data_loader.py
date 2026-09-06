from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from pathlib import Path

import csv


@dataclass(frozen=True)
class EnvironmentRecord:
    observed_month: date
    rainfall_mm: float
    ndvi: float
    water_percent: float


DEMO_RECORDS = (
    EnvironmentRecord(date(2025, 1, 1), 18, 0.42, 2.8),
    EnvironmentRecord(date(2025, 2, 1), 26, 0.45, 2.9),
    EnvironmentRecord(date(2025, 3, 1), 54, 0.49, 3.0),
    EnvironmentRecord(date(2025, 4, 1), 112, 0.53, 3.4),
    EnvironmentRecord(date(2025, 5, 1), 238, 0.56, 4.0),
    EnvironmentRecord(date(2025, 6, 1), 421, 0.58, 4.7),
    EnvironmentRecord(date(2025, 7, 1), 468, 0.61, 5.1),
    EnvironmentRecord(date(2025, 8, 1), 342, 0.60, 5.0),
    EnvironmentRecord(date(2025, 9, 1), 246, 0.57, 4.6),
    EnvironmentRecord(date(2025, 10, 1), 128, 0.53, 4.0),
    EnvironmentRecord(date(2025, 11, 1), 39, 0.48, 3.3),
    EnvironmentRecord(date(2025, 12, 1), 17, 0.44, 2.9),
    EnvironmentRecord(date(2026, 1, 1), 21, 0.43, 2.8),
    EnvironmentRecord(date(2026, 2, 1), 30, 0.46, 2.9),
    EnvironmentRecord(date(2026, 3, 1), 61, 0.50, 3.1),
    EnvironmentRecord(date(2026, 4, 1), 118, 0.54, 3.5),
    EnvironmentRecord(date(2026, 5, 1), 251, 0.57, 4.2),
    EnvironmentRecord(date(2026, 6, 1), 421, 0.58, 4.7),
)


def load_records(csv_path: Path | None = None) -> tuple[EnvironmentRecord, ...]:
    """Load government-prepared records when present; otherwise use demo records."""
    if csv_path is None:
        csv_path = Path(__file__).parents[2] / "data" / "historical_environment.csv"

    if not csv_path.exists():
        return DEMO_RECORDS

    with csv_path.open(newline="", encoding="utf-8") as file:
        reader = csv.DictReader(file)
        return tuple(
            EnvironmentRecord(
                observed_month=date.fromisoformat(row["observed_month"]),
                rainfall_mm=float(row["rainfall_mm"]),
                ndvi=float(row["ndvi"]),
                water_percent=float(row["water_percent"]),
            )
            for row in reader
        )


def data_source(csv_path: Path | None = None) -> str:
    if csv_path is None:
        csv_path = Path(__file__).parents[2] / "data" / "historical_environment.csv"
    return "government_csv" if csv_path.exists() else "demo_dataset"