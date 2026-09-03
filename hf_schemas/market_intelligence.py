from pydantic import BaseModel, Field


class MarketIntelligenceOutput(BaseModel):

    volatility_regime: str = Field(
        description="Classify volatility as low, moderate, or high"
    )

    volume_signal: str = Field(
        description="Classify volume as high, normal, or low based on current volume and historical volume"
    )

    market_bias: str = Field(
        description="Overall market bias: bullish, bearish, or neutral"
    )

    analysis: str = Field(
        description="Concise market intelligence summary based on all supplied market metrics"
    )