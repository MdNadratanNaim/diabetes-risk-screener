from pydantic import BaseModel, Field
from typing import Optional


class DiabetesRiskInput(BaseModel):
    """
    Full BRFSS 2015 feature set. If your trained model uses a smaller subset,
    leave this as-is — main.py only pulls the fields listed in the model's
    saved feature_order, so extra fields here are harmless.
    """
    HighBP: int = Field(..., ge=0, le=1)
    HighChol: int = Field(..., ge=0, le=1)
    CholCheck: int = Field(..., ge=0, le=1)
    BMI: float = Field(..., gt=0, le=100)
    Smoker: int = Field(..., ge=0, le=1)
    Stroke: int = Field(..., ge=0, le=1)
    HeartDiseaseorAttack: int = Field(..., ge=0, le=1)
    PhysActivity: int = Field(..., ge=0, le=1)
    Fruits: int = Field(..., ge=0, le=1)
    Veggies: int = Field(..., ge=0, le=1)
    HvyAlcoholConsump: int = Field(..., ge=0, le=1)
    AnyHealthcare: int = Field(..., ge=0, le=1)
    NoDocbcCost: int = Field(..., ge=0, le=1)
    GenHlth: int = Field(..., ge=1, le=5)       # 1=excellent ... 5=poor
    MentHlth: int = Field(..., ge=0, le=30)      # days in past 30
    PhysHlth: int = Field(..., ge=0, le=30)      # days in past 30
    DiffWalk: int = Field(..., ge=0, le=1)
    Sex: int = Field(..., ge=0, le=1)
    Age: int = Field(..., ge=1, le=13)           # BRFSS age bracket code
    Education: int = Field(..., ge=1, le=6)
    Income: int = Field(..., ge=1, le=8)


class RiskResponse(BaseModel):
    probability: float
    risk_category: str
    top_factors: Optional[list] = None


class RiskResponse(BaseModel):
    probability: float
    confidence: float
    risk_category: str      # "low" | "moderate" | "high" — drives CSS class
    risk_label: str         # "Low Risk" | "Elevated Risk" | "High Risk" — display text
    top_factors: Optional[list] = None
    recommendations: Optional[list] = None