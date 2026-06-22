from tools.market_data_tools import get_market_data
from hf_schemas.market_intelligence import MarketIntelligenceOutput
from pydantic import BaseModel, Field
from langchain_core.output_parsers import PydanticOutputParser
from langchain_core.prompts import PromptTemplate
from langchain_groq import ChatGroq

from dotenv import load_dotenv
import os

load_dotenv()

# --------------------------------------------------
# 1️⃣ LLM
# --------------------------------------------------
llm = ChatGroq(
    model="llama-3.1-8b-instant",
    temperature=0
)

# --------------------------------------------------
# 2️⃣ Load prompt
# --------------------------------------------------
def load_prompt() -> str:
    with open("prompts/market_intelligence.txt", "r", encoding="utf-8") as f:
        return f.read()

prompt_text = load_prompt()

parser = PydanticOutputParser(pydantic_object=MarketIntelligenceOutput)

# --------------------------------------------------
# 4️⃣ Prompt template
# --------------------------------------------------
template = PromptTemplate(
    template=prompt_text,
    input_variables=["stock_symbol", "market_data"],
    partial_variables={
        "format_instruction": parser.get_format_instructions()
    }
)

# --------------------------------------------------
# 5️⃣ Chain
# --------------------------------------------------
chain = template | llm | parser

# --------------------------------------------------
# 6️⃣ Confidence scoring
# --------------------------------------------------
def compute_confidence(data):
    if not data or "error" in data:
        return "low"

    valid = sum(v not in [None, 0, ""] for v in data.values())
    total = len(data)

    ratio = valid / total if total else 0

    if ratio > 0.7:
        return "high"
    elif ratio > 0.4:
        return "medium"
    else:
        return "low"

# --------------------------------------------------
# 7️⃣ Agent
# --------------------------------------------------
def market_intelligence_agent(state):
    symbol = state["stock_symbol"]

    market_data = get_market_data(symbol)

    # 🔴 HARD VALIDATION
    if market_data.get("error"):
        return {
            "market_intelligence": {
                "stock": symbol,
                "analysis": "Market data unavailable due to API limits or temporary issues.",
                "raw_data": market_data,
                "confidence": "low"
            }
        }

    # 🔹 LLM analysis
    result = chain.invoke({
        "stock_symbol": symbol,
        "market_data": market_data
    })

    # 🔹 Confidence
    confidence = compute_confidence(market_data)

    # 🔹 Volume signal
    volume = market_data.get("volume", 0)
    volume_signal = "high" if volume > 1_000_000 else "normal"

    # 🔹 Market bias
    if result.trend == "uptrend":
        bias = "bullish"
    elif result.trend == "downtrend":
        bias = "bearish"
    else:
        bias = "neutral"

    return {
        "market_intelligence": {
            "signals": {
                "trend": result.trend,
                "momentum": result.momentum,
                "volatility_regime": result.volatility_regime,  # ✅ FIXED
                "percent_change": market_data.get("percent_change"),
                "volume_signal": volume_signal,                 # ✅ ADDED
                "market_bias": bias                             # ✅ FIXED
            },
            "analysis": result.analysis,
            "confidence": confidence,
            "raw_data": market_data
        }
    }