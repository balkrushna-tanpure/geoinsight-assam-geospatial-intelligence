from __future__ import annotations

from datetime import date
from urllib.parse import urlencode
from urllib.request import urlopen
import json

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from .database import save_training_run
from .data_loader import data_source, load_records
from .ml_model import EnvironmentalForecaster

app = FastAPI(title="GeoInsight API", version="0.1.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

records = load_records()
forecaster = EnvironmentalForecaster(records)
training_saved = save_training_run("Kamrup", data_source(), "RandomForestRegressor baseline", forecaster.validation)
DISTRICTS = (
    {"name": "Kamrup", "state": "Assam", "latitude": 26.1445, "longitude": 91.7362, "area_km2": 4345, "rain_factor": 1.0, "ndvi_factor": 1.0, "water_factor": 1.0},
    {"name": "Kamrup Metropolitan", "state": "Assam", "latitude": 26.1445, "longitude": 91.7362, "area_km2": 955, "rain_factor": 0.92, "ndvi_factor": 0.96, "water_factor": 0.82},
    {"name": "Dibrugarh", "state": "Assam", "latitude": 27.4728, "longitude": 94.912, "area_km2": 3381, "rain_factor": 1.08, "ndvi_factor": 1.04, "water_factor": 1.16},
)


@app.get("/api/v1/health")
def health() -> dict[str, str]:
    return {"status": "ok", "service": "geoinsight-api"}


@app.get("/api/v1/districts")
def districts() -> dict[str, object]:
    return {"districts": DISTRICTS}


@app.get("/api/v1/live")
def live_weather(district: str = "kamrup") -> dict[str, object]:
    selected = next((item for item in DISTRICTS if item["name"].lower() == district.lower()), None)
    if selected is None:
        raise HTTPException(status_code=404, detail="District is not available in this prototype")
    query = urlencode({"latitude": selected["latitude"], "longitude": selected["longitude"], "current": "temperature_2m,relative_humidity_2m,precipitation,rain,wind_speed_10m,weather_code", "timezone": "Asia/Kolkata"})
    try:
        with urlopen(f"https://api.open-meteo.com/v1/forecast?{query}", timeout=8) as response:
            payload = json.load(response)
        return {"district": selected["name"], "source": "Open-Meteo live weather", "current": payload["current"]}
    except Exception as error:
        raise HTTPException(status_code=503, detail=f"Live weather is temporarily unavailable: {error}") from error


@app.get("/api/v1/prediction")
def prediction(
    district: str = "kamrup",
    month: str = "2026-07",
) -> dict[str, object]:
    selected_district = next((item for item in DISTRICTS if item["name"].lower() == district.lower()), None)
    if selected_district is None:
        raise HTTPException(status_code=404, detail="District is not available in this prototype")
    try:
        target_month = date.fromisoformat(f"{month}-01")
    except ValueError as error:
        raise HTTPException(status_code=400, detail="month must be a valid YYYY-MM value") from error

    base_prediction = forecaster.predict(target_month)
    predicted = {
        **base_prediction,
        "rainfall_mm": round(float(base_prediction["rainfall_mm"]) * selected_district["rain_factor"], 1),
        "ndvi": round(min(1, float(base_prediction["ndvi"]) * selected_district["ndvi_factor"]), 3),
        "water_percent": round(float(base_prediction["water_percent"]) * selected_district["water_factor"], 2),
    }
    predicted["water_area_km2"] = round(selected_district["area_km2"] * predicted["water_percent"] / 100, 1)
    rainfall_value = float(predicted["rainfall_mm"])
    risks = {
        "flood_risk": "high" if rainfall_value >= 400 else "moderate" if rainfall_value >= 200 else "low",
        "drought_risk": "high" if rainfall_value < 60 else "moderate" if rainfall_value < 150 else "low",
        "crop_stress": "high" if float(predicted["ndvi"]) < 0.35 else "moderate" if float(predicted["ndvi"]) < 0.5 else "low",
    }
    return {
        "district": selected_district["name"],
        "state": selected_district["state"],
        "prediction": predicted,
        "risks": risks,
        "rainfall_history": [
            {"month": record.observed_month.strftime("%Y-%m"), "rainfall_mm": round(record.rainfall_mm * selected_district["rain_factor"], 1)}
            for record in records
        ],
        "training_records": len(records),
        "data_source": data_source(),
        "note": "Demo district profiles are used until government-validated district datasets are loaded.",
    }


@app.get("/api/v1/model/validation")
def model_validation() -> dict[str, object]:
    return {
        "district": "Kamrup",
        "model": "RandomForestRegressor baseline",
        "data_source": data_source(),
        "database_saved": training_saved,
        "validation": forecaster.validation,
    }