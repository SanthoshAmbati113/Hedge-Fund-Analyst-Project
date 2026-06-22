from pydantic import BaseModel, Field
from typing import List


class Scenario(BaseModel):
    title: str
    probability: str  # low / medium / high
    explanation: str


class RiskAssessment(BaseModel):
    overall_risk_score: int = Field(description="0-100 risk score")
    risk_level: str = Field(description="low | medium | high")

    key_risks: List[str]
    key_drivers: List[str]

    bull_scenario: Scenario
    bear_scenario: Scenario

    confidence: str = Field(description="low | medium | high")
    summary: str