from pydantic import BaseModel, Field
from typing import List


class ThesisPoint(BaseModel):

    title: str = Field(
        description="Specific title of the thesis point"
    )

    explanation: str = Field(
        description="Why this point matters"
    )

    evidence: List[str] = Field(
        description="Evidence from the upstream analyses supporting this point"
    )


class InvestmentThesis(BaseModel):

    stock_name: str

    recommendation: str = Field(
        description="bullish, neutral, or bearish"
    )

    conviction: str = Field(
        description="high, medium, or low"
    )

    risk_level: str = Field(
        description="low, medium, or high"
    )

    risk_score: float = Field(
        description="Overall risk score from the risk assessment, between 0 and 100"
    )

    bull_case: List[ThesisPoint] = Field(
        description="Two to three strongest arguments supporting the bullish thesis"
    )

    bear_case: List[ThesisPoint] = Field(
        description="Two to three strongest arguments supporting the bearish thesis"
    )

    key_catalysts: List[str] = Field(
        description="Important catalysts explicitly supported by the provided analyses"
    )

    key_risks: List[str] = Field(
        description="Three to five most material risks"
    )

    valuation_view: str = Field(
        description="cheap, fair, or expensive, with justification"
    )

    risk_reward_summary: str = Field(
        description="Assessment of upside versus downside risk"
    )

    final_summary: str = Field(
        description="Four to six sentence final investment thesis"
    )