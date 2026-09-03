from pydantic import BaseModel, Field
from typing import List


class Scenario(BaseModel):

    title: str = Field(
        description="Short title describing the scenario"
    )

    probability: float = Field(
        description="Estimated probability between 0 and 100"
    )

    explanation: str = Field(
        description="Explanation grounded only in the supplied analyses"
    )


class RiskAssessment(BaseModel):

    overall_risk_score: float = Field(
        description="Overall current risk score from 0 to 100"
    )

    risk_level: str = Field(
        description="low, medium, or high"
    )

    key_risks: List[str] = Field(
        description="At least 3 specific risks supported by the inputs"
    )

    key_drivers: List[str] = Field(
        description="At least 3 important factors currently shaping risk"
    )

    bull_scenario: Scenario = Field(
        description="Scenario describing what goes right"
    )

    bear_scenario: Scenario = Field(
        description="Scenario describing what goes wrong"
    )

    confidence: str = Field(
        description="high, medium, or low"
    )

    summary: str = Field(
        description="Concise integrated assessment of the current risk profile"
    )