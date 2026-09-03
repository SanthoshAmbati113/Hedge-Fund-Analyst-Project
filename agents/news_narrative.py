from tools.news_tools import get_company_news

from pydantic import BaseModel, Field
from typing import List

from langchain_core.output_parsers import PydanticOutputParser
from langchain_core.prompts import PromptTemplate
from langchain_groq import ChatGroq

from dotenv import load_dotenv
from pathlib import Path


# ============================================================
# ENVIRONMENT
# ============================================================

load_dotenv(
    Path(__file__).resolve().parents[1] / ".env"
)


# ============================================================
# LLM
# ============================================================

llm = ChatGroq(
    model="openai/gpt-oss-20b",
    temperature=0
)


# ============================================================
# SCHEMA
# ============================================================

class NewsNarrativeOutput(BaseModel):

    sentiment: str = Field(
        description=(
            "Overall sentiment of the recent news flow: "
            "bullish, bearish, or neutral"
        )
    )

    dominant_themes: List[str] = Field(
        description=(
            "The major recurring themes identified across "
            "the news articles"
        )
    )

    key_events: List[str] = Field(
        description=(
            "The most important concrete events or "
            "developments mentioned across the news"
        )
    )

    narrative_direction: str = Field(
        description=(
            "Overall direction of the news narrative, "
            "such as positive, negative, mixed, or neutral"
        )
    )

    time_horizon: str = Field(
        description=(
            "Primary time horizon of the reported developments, "
            "such as immediate, short-term, medium-term, "
            "or long-term"
        )
    )

    confidence: str = Field(
        description=(
            "Confidence in the synthesized news narrative: "
            "high, medium, or low"
        )
    )

    summary: str = Field(
        description=(
            "Detailed but concise synthesis of the entire "
            "recent news flow, combining the key developments, "
            "themes, sentiment, and important context"
        )
    )


# ============================================================
# OUTPUT PARSER
# ============================================================

parser = PydanticOutputParser(
    pydantic_object=NewsNarrativeOutput
)


# ============================================================
# LOAD PROMPT
# ============================================================

def load_prompt():

    with open(
        "prompts/news_narrative.txt",
        "r",
        encoding="utf-8"
    ) as f:

        return f.read()


# ============================================================
# PROMPT TEMPLATE
# ============================================================

template = PromptTemplate(

    template=load_prompt(),

    input_variables=[
        "company",
        "news_data"
    ],

    partial_variables={
        "format_instruction":
            parser.get_format_instructions()
    }
)


# ============================================================
# CHAIN
# ============================================================

chain = (
    template
    | llm
    | parser
)


# ============================================================
# CONFIDENCE LOGIC
# ============================================================

def compute_confidence(news_items):

    if not news_items:
        return "low"

    article_count = len(news_items)

    if article_count >= 10:
        return "high"

    elif article_count >= 5:
        return "medium"

    else:
        return "low"


# ============================================================
# NEWS NARRATIVE AGENT
# ============================================================

def news_narrative_agent(state):

    # --------------------------------------------------------
    # Get stock symbol
    # --------------------------------------------------------

    symbol = state.get("stock_symbol")

    if not symbol:

        raise ValueError(
            "No valid stock symbol provided"
        )


    # --------------------------------------------------------
    # Get company name if available
    # Used only for LLM context
    # --------------------------------------------------------

    company = (
        state.get("stock_name")
        or symbol
    )


    # ========================================================
    # STEP 1: FETCH NEWS
    # ========================================================

    news_items = get_company_news(

        symbol=symbol,

        max_results=15,

        candidate_limit=30
    )


    # ========================================================
    # STEP 2: HANDLE NO NEWS
    # ========================================================

    if not news_items:

        return {

            "news_narrative": {

                "sentiment": "neutral",

                "dominant_themes": [],

                "key_events": [],

                "narrative_direction": "uncertain",

                "time_horizon": "short-term",

                "confidence": "low",

                "summary": (
                    "No recent relevant news articles "
                    "were retrieved for this stock."
                ),

                "raw_news": []

            }
        }


    # ========================================================
    # STEP 3: SEND ALL 15 ARTICLES TO LLM
    # ========================================================

    result = chain.invoke({

        "company": company,

        "news_data": news_items
    })


    # ========================================================
    # STEP 4: COMPUTE DATA CONFIDENCE
    # ========================================================

    confidence = compute_confidence(
        news_items
    )


    # ========================================================
    # STEP 5: RETURN SYNTHESIZED NEWS INTELLIGENCE
    # ========================================================

    return {

        "news_narrative": {

            # ------------------------------------------------
            # OVERALL SENTIMENT
            # ------------------------------------------------

            "sentiment":
                result.sentiment,


            # ------------------------------------------------
            # MAJOR THEMES
            # ------------------------------------------------

            "dominant_themes":
                result.dominant_themes,


            # ------------------------------------------------
            # IMPORTANT EVENTS
            # ------------------------------------------------

            "key_events":
                result.key_events,


            # ------------------------------------------------
            # NEWS DIRECTION
            # ------------------------------------------------

            "narrative_direction":
                result.narrative_direction,


            # ------------------------------------------------
            # TIME HORIZON
            # ------------------------------------------------

            "time_horizon":
                result.time_horizon,


            # ------------------------------------------------
            # CONFIDENCE
            # ------------------------------------------------

            "confidence":
                confidence,


            # ------------------------------------------------
            # COMBINED NEWS SUMMARY
            # ------------------------------------------------

            "summary":
                result.summary,


            # ------------------------------------------------
            # RAW ARTICLES
            # ------------------------------------------------

            "raw_news":
                news_items
        }
    }