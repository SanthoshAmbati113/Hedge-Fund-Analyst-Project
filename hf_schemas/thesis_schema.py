from pydantic import BaseModel, Field
from typing import List


class ThesisPoint(BaseModel):
    title: str
    explanation: str
    evidence: List[str]


class InvestmentThesis(BaseModel):
    stock_name: str

    recommendation: str = Field(description="bullish | neutral | bearish")
    conviction: str = Field(description="low | medium | high")

    # 🔥 ADD THIS (CRITICAL)
    risk_level: str
    risk_score: int

    bull_case: List[ThesisPoint]
    bear_case: List[ThesisPoint]

    key_catalysts: List[str]
    key_risks: List[str]

    valuation_view: str

    # 🔥 IMPROVED
    risk_reward_summary: str

    # 🔥 FINAL DECISION SUMMARY
    final_summary: str