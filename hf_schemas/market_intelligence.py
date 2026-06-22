from pydantic import BaseModel,Field
class MarketIntelligenceOutput(BaseModel):
    # stock_symbol: str = Field(description="Ticker symbol (e.g., AAPL)")

    # 🔥 Directional signals
    trend: str = Field(description="uptrend, downtrend, or sideways")
    momentum: str = Field(description="positive, negative, or neutral")
    volatility_regime: str = Field(description="low, moderate, or high volatility")

    # 🔥 NUMERICAL SIGNALS (CRITICAL)
    percent_change: float = Field(description="Recent price % change")
    volume_signal: str = Field(description="high, normal, or low volume vs average")

    # 🔥 INTERPRETABLE SIGNAL
    market_bias: str = Field(description="bullish, bearish, or neutral bias")

    # Summary
    analysis: str = Field(description="Concise market intelligence summary")