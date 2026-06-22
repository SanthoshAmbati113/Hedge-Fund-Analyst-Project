from tools.fundamental_tools import get_fundamentals

from pydantic import BaseModel, Field
from langchain_core.output_parsers import PydanticOutputParser
from langchain_core.prompts import PromptTemplate
from langchain_groq import ChatGroq

from dotenv import load_dotenv
from pathlib import Path

load_dotenv(Path(__file__).resolve().parents[1] / ".env")


# --------------------------------------------------
# 1️⃣ LLM
# --------------------------------------------------
llm = ChatGroq(
    model="llama-3.1-8b-instant",
    temperature=0
)


# --------------------------------------------------
# 2️⃣ Output schema (UPDATED)
# --------------------------------------------------
class FundamentalsOutput(BaseModel):
    profitability: str
    financial_health: str
    valuation: str
    growth: str
    overall_strength: str
    confidence: str
    summary: str


parser = PydanticOutputParser(pydantic_object=FundamentalsOutput)


# --------------------------------------------------
# 3️⃣ Prompt loader
# --------------------------------------------------
def load_prompt() -> str:
    with open("prompts/fundamental_analysis.txt", "r", encoding="utf-8") as f:
        return f.read()


prompt_text = load_prompt()


# --------------------------------------------------
# 4️⃣ Prompt template
# --------------------------------------------------
template = PromptTemplate(
    template=prompt_text,
    input_variables=["stock_symbol", "fundamentals_data"],
    partial_variables={
        "format_instruction": parser.get_format_instructions()
    }
)

chain = template | llm | parser


# --------------------------------------------------
# 🔥 5️⃣ Improved confidence (CORE vs SECONDARY)
# --------------------------------------------------
def compute_confidence(data):

    if not data or "error" in data:
        return "low"

    # 🔹 Core signals (important)
    core_fields = [
        data.get("revenue"),
        data.get("profit_margin"),
        data.get("roe"),
        data.get("pe_ratio"),
        data.get("pb_ratio"),
        data.get("revenue_growth")
    ]

    # 🔹 Secondary signals
    secondary_fields = [
        data.get("operating_margin"),
        data.get("roa"),
        data.get("peg_ratio"),
        data.get("dividend_yield"),
        data.get("earnings_growth")
    ]

    core_filled = sum(x is not None for x in core_fields)
    secondary_filled = sum(x is not None for x in secondary_fields)

    if core_filled >= 4:
        return "high"
    elif core_filled >= 2:
        return "medium"
    else:
        return "low"


# --------------------------------------------------
# 6️⃣ Agent
# --------------------------------------------------
def fundamentals_agent(state):

    stock = state["stock_symbol"]

    fundamentals_data = get_fundamentals(stock)

    # 🔴 HARD VALIDATION
    if not fundamentals_data or "error" in fundamentals_data:
        return {
            "fundamental_analysis": {
                "signals": {
                    "profitability": "Data unavailable",
                    "financial_health": "Data unavailable",
                    "valuation": "Data unavailable",
                    "growth": "Data unavailable",
                    "overall_strength": "unclear",
                    "confidence": "low",
                },
                "summary": "Fundamental data could not be retrieved.",
                "raw_data": fundamentals_data
            }
        }

    # 🔹 Compute deterministic confidence
    confidence = compute_confidence(fundamentals_data)

    # 🔹 Run LLM
    result = chain.invoke({
        "stock_symbol": stock,
        "fundamentals_data": fundamentals_data
    })

    # 🔴 Override LLM confidence
    result.confidence = confidence

    return {
        "fundamental_analysis": {
            "signals": {
                "profitability": result.profitability,
                "financial_health": result.financial_health,
                "valuation": result.valuation,
                "growth": result.growth,
                "overall_strength": result.overall_strength,
                "confidence": result.confidence,
            },
            "summary": result.summary,
            "raw_data": fundamentals_data
        }
    }