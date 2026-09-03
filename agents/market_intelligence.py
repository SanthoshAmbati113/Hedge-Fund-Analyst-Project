from tools.market_data_tools import get_market_data
from hf_schemas.market_intelligence import MarketIntelligenceOutput

from langchain_core.output_parsers import PydanticOutputParser
from langchain_core.prompts import PromptTemplate
from langchain_groq import ChatGroq
import os

from dotenv import load_dotenv

load_dotenv()


# ============================================================
# 1. LLM
# ============================================================

llm = ChatGroq(
    model="openai/gpt-oss-20b",
    temperature=0,
    
)


# ============================================================
# 2. LOAD PROMPT
# ============================================================

def load_prompt() -> str:

    with open(
        "prompts/market_intelligence.txt",
        "r",
        encoding="utf-8"
    ) as f:
        return f.read()


prompt_text = load_prompt()


# ============================================================
# 3. OUTPUT PARSER
# ============================================================

parser = PydanticOutputParser(
    pydantic_object=MarketIntelligenceOutput
)


# ============================================================
# 4. PROMPT TEMPLATE
# ============================================================

template = PromptTemplate(
    template=prompt_text,

    input_variables=[
        "stock_symbol",
        "market_data"
    ],

    partial_variables={
        "format_instruction":
            parser.get_format_instructions()
    }
)


# ============================================================
# 5. LLM CHAIN
# ============================================================

chain = template | llm | parser


# ============================================================
# 6. CONFIDENCE
# ============================================================

def compute_confidence(data):

    if not data or "error" in data:
        return "low"

    required_metrics = [
        "price",
        "change",
        "percent_change",
        "volume",
        "return_3m",
        "return_6m",
        "return_1y",
        "volatility",
        "ma_4",
        "ma_12",
        "ma_26",
        
    ]

    valid = sum(
        data.get(metric) is not None
        for metric in required_metrics
    )

    ratio = valid / len(required_metrics)

    if ratio >= 0.8:
        return "high"

    elif ratio >= 0.5:
        return "medium"

    else:
        return "low"


# ============================================================
# 7. MARKET INTELLIGENCE AGENT
# ============================================================

def market_intelligence_agent(state):

    symbol = state["stock_symbol"]


    # ========================================================
    # STEP 1: GET MARKET DATA FROM TOOL
    # ========================================================

    market_data = get_market_data(symbol)


    # ========================================================
    # STEP 2: HANDLE API FAILURE
    # ========================================================

    if market_data.get("error"):

        return {
            "market_intelligence": {
                "stock": symbol,
                "error": market_data["error"],
                "analysis": (
                    "Market data is currently unavailable "
                    "due to an API or data retrieval issue."
                ),
                "raw_data": market_data,
                "confidence": "low"
            }
        }


    # ========================================================
    # STEP 3: SEND ALL MARKET METRICS TO LLM
    # ========================================================

    result = chain.invoke({

        "stock_symbol": symbol,

        "market_data": market_data
    })


    # ========================================================
    # STEP 4: CONFIDENCE
    # ========================================================

    confidence = compute_confidence(
        market_data
    )


    # ========================================================
    # STEP 5: RETURN TOOL VALUES + LLM ANALYSIS
    # ========================================================

    return {

        "market_intelligence": {

            "stock": symbol,

            # ------------------------------------------------
            # VALUES DIRECTLY FROM MARKET TOOL
            # ------------------------------------------------

            "price": market_data["price"],

            "change": market_data["change"],

            "percent_change":
                market_data["percent_change"],

            "volume":
                market_data["volume"],

            "return_3m":
                market_data["return_3m"],

            "return_6m":
                market_data["return_6m"],

            "return_1y":
                market_data["return_1y"],

            "volatility":
                market_data["volatility"],

            "ma_4":
                market_data["ma_4"],

            "ma_12":
                market_data["ma_12"],

            "ma_26":
                market_data["ma_26"],
                
            "trend":
                market_data["trend"],
            
            "momentum":
                market_data["momentum"],     

            


            # ------------------------------------------------
            # INTERPRETATION FROM LLM
            # ------------------------------------------------

            "signals": {


                "volatility_regime":
                    result.volatility_regime,

                "volume_signal":
                    result.volume_signal,

                "market_bias":
                    result.market_bias
            },


            # ------------------------------------------------
            # LLM ANALYSIS
            # ------------------------------------------------

            "analysis":
                result.analysis,


            # ------------------------------------------------
            # METADATA
            # ------------------------------------------------

            "confidence":
                confidence,

            "source":
                market_data.get(
                    "source",
                    "alpha_vantage"
                ),

            "raw_data":
                market_data
        }
    }