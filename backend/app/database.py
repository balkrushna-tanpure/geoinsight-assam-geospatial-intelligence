from __future__ import annotations

import json
import os
from pathlib import Path

from dotenv import load_dotenv

try:
    import psycopg
except ImportError:  # The API can still run with demo data before dependencies are installed.
    psycopg = None

load_dotenv(Path(__file__).parents[1] / ".env")


def save_training_run(district: str, source: str, model_name: str, validation: dict[str, object]) -> bool:
    if psycopg is None or not os.getenv("DATABASE_URL"):
        return False
    metrics = validation["metrics"]
    with psycopg.connect(os.environ["DATABASE_URL"]) as connection:
        connection.execute(
            """
            INSERT INTO model_training_runs
                (district_name, model_name, training_source, train_records, test_records, test_period, metrics)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            """,
            (district, model_name, source, validation["train_records"], validation["test_records"], validation["test_period"]["from"] + " to " + validation["test_period"]["to"], json.dumps(metrics)),
        )
    return True