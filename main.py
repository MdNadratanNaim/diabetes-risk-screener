import json
import math
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse, Response
from fastapi.templating import Jinja2Templates
from typing import Annotated

from app.schema import DiabetesRiskInput, RiskResponse  # requires app/__init__.py + app/schema.py

FEATURE_LABELS = {
    "HighBP": "High Blood Pressure", "HighChol": "High Cholesterol",
    "CholCheck": "Cholesterol Checked (Past 5 Years)", "BMI": "BMI",
    "Smoker": "Smoker", "Stroke": "Previous Stroke",
    "HeartDiseaseorAttack": "Heart Disease or Heart Attack",
    "PhysActivity": "Physical Activity", "Fruits": "Eats Fruit Regularly",
    "Veggies": "Eats Vegetables Regularly", "HvyAlcoholConsump": "Heavy Alcohol Consumption",
    "AnyHealthcare": "Has Healthcare Coverage", "NoDocbcCost": "Couldn't See Doctor Due to Cost",
    "GenHlth": "General Health", "MentHlth": "Poor Mental Health Days",
    "PhysHlth": "Poor Physical Health Days", "DiffWalk": "Difficulty Walking",
    "Sex": "Gender", "Age": "Age Group", "Education": "Education Level", "Income": "Income Level",
}

RISK_LABELS = {"low": "Low Risk", "moderate": "Elevated Risk", "high": "High Risk"}

RECOMMENDATION_RULES = {
    "BMI": "Aim for 30 minutes of activity most days",
    "HighBP": "Get your blood pressure checked regularly",
    "HighChol": "Ask your doctor about a cholesterol screening",
    "GenHlth": "Schedule a general checkup",
    "PhysHlth": "Talk to a doctor about ongoing physical symptoms",
    "MentHlth": "Consider talking to a mental health professional",
    "Smoker": "Consider a smoking cessation program",
    "HvyAlcoholConsump": "Consider reducing alcohol intake",
    "DiffWalk": "Ask your doctor about a mobility assessment",
}
GENERIC_RECOMMENDATION = "Annual diabetes screening"


app = FastAPI(title="Diabetes Risk Screener")
BASE_DIR = Path(__file__).resolve().parent  # main.py lives at the project root
templates = Jinja2Templates(directory=str(BASE_DIR / "app" / "templates"))

MODEL_DIR = BASE_DIR / "model"
MODEL_PATH = MODEL_DIR / "model.pkl"
METADATA_PATH = MODEL_DIR / "model_metadata.json"

model = joblib.load(MODEL_PATH)

with open(METADATA_PATH) as f:
    metadata = json.load(f)

feature_order = metadata["features"]
threshold = metadata["decision_threshold"]
risk_buckets = metadata.get("risk_buckets", {"low": threshold / 2, "moderate": threshold})

explainer = None
preprocessor = None
final_estimator = model
try:
    import shap
    if hasattr(model, "steps"):
        final_estimator = model.steps[-1][1]
        if len(model.steps) > 1:
            preprocessor = model[:-1]

    if hasattr(final_estimator, "feature_importances_"):
        explainer = shap.TreeExplainer(final_estimator)
    elif hasattr(final_estimator, "coef_"):
        zeros = pd.DataFrame(np.zeros((1, len(feature_order))), columns=feature_order)
        background = preprocessor.transform(zeros) if preprocessor is not None else zeros
        explainer = shap.LinearExplainer(final_estimator, background)
except Exception:
    explainer = None


def compute_confidence(prob: float) -> float:
    """How decisively the model landed on this probability, via binary entropy."""
    p = min(max(prob, 1e-6), 1 - 1e-6)
    entropy = -(p * math.log2(p) + (1 - p) * math.log2(1 - p))
    return round((1 - entropy) * 100, 1)


def get_top_factors(row: pd.DataFrame, n: int = 3) -> list:
    if explainer is None:
        return []
    try:
        transformed = preprocessor.transform(row) if preprocessor is not None else row
        raw = explainer.shap_values(transformed)
        if isinstance(raw, list):
            values = np.array(raw[1]).flatten()
        else:
            arr = np.array(raw)
            values = arr[..., 1].flatten() if arr.ndim == 3 else arr.flatten()
        idx = np.argsort(np.abs(values))[::-1][:n]
        return [
            {
                "feature": feature_order[i],
                "label": FEATURE_LABELS.get(feature_order[i], feature_order[i]),
                "impact": round(float(values[i]), 4),
            }
            for i in idx
        ]
    except Exception:
        return []


def build_recommendations(top_factors: list, risk_category: str) -> list:
    recs = []
    for f in top_factors:
        rule = RECOMMENDATION_RULES.get(f["feature"])
        if rule and rule not in recs:
            recs.append(rule)
    if risk_category != "low" and GENERIC_RECOMMENDATION not in recs:
        recs.append(GENERIC_RECOMMENDATION)
    return recs[:4]


def bucket_risk(prob: float) -> str:
    if prob < risk_buckets["low"]:
        return "low"
    if prob < risk_buckets["moderate"]:
        return "moderate"
    return "high"


def run_prediction(payload: dict) -> RiskResponse:
    row = pd.DataFrame([[payload[f] for f in feature_order]], columns=feature_order)
    prob = float(model.predict_proba(row)[0, 1])
    category = bucket_risk(prob)
    top_factors = get_top_factors(row)

    return RiskResponse(
        probability=round(prob, 4),
        confidence=compute_confidence(prob),
        risk_category=category,
        risk_label=RISK_LABELS[category],
        top_factors=top_factors,
        recommendations=build_recommendations(top_factors, category),
    )


@app.get("/", response_class=HTMLResponse)
def form_page(request: Request):
    return templates.TemplateResponse(request, "index.html", {"result": None})


@app.post("/predict", response_class=HTMLResponse)
def predict_form(request: Request, data: Annotated[DiabetesRiskInput, Form()]):
    result = run_prediction(data.model_dump())
    return templates.TemplateResponse(request, "index.html", {"result": result})


@app.post("/api/predict", response_model=RiskResponse)
def predict_api(data: DiabetesRiskInput):
    """Same logic, JSON in/out — this is what shows up in /docs for your CV demo."""
    return run_prediction(data.model_dump())

FAVICON_PATH = BASE_DIR / "app" / "templates" / "favicon.ico"
FAVICON_BYTES = FAVICON_PATH.read_bytes() if FAVICON_PATH.exists() else None


@app.get("/favicon.ico", include_in_schema=False)
async def favicon():
    if FAVICON_BYTES is None:
        return HTMLResponse(status_code=404, content="")
    # Serve from memory rather than re-reading the file on every request.
    return Response(content=FAVICON_BYTES, media_type="image/x-icon")
