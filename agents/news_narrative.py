from tools.news_tools import get_company_news

from pydantic import BaseModel, Field
from typing import List
from langchain_core.output_parsers import PydanticOutputParser
from langchain_core.prompts import PromptTemplate
from langchain_groq import ChatGroq

from dotenv import load_dotenv
from pathlib import Path

load_dotenv(Path(__file__).resolve().parents[1] / ".env")


# --------------------------------------------------
# LLM
# --------------------------------------------------
llm = ChatGroq(
    model="llama-3.1-8b-instant",
    temperature=0
)


# --------------------------------------------------
# Schema
# --------------------------------------------------
class NewsNarrativeOutput(BaseModel):
    sentiment: str
    dominant_themes: List[str]
    key_events: List[str]
    narrative_direction: str
    time_horizon: str
    confidence: str
    summary: str


parser = PydanticOutputParser(pydantic_object=NewsNarrativeOutput)


# --------------------------------------------------
# Prompt
# --------------------------------------------------
def load_prompt():
    with open("prompts/news_narrative.txt", "r", encoding="utf-8") as f:
        return f.read()


template = PromptTemplate(
    template=load_prompt(),
    input_variables=["company", "news_data"],
    partial_variables={
        "format_instruction": parser.get_format_instructions()
    }
)

chain = template | llm | parser


# --------------------------------------------------
# Confidence logic
# --------------------------------------------------
def compute_confidence(news_items):
    if not news_items:
        return "low"

    if len(news_items) >= 5:
        return "high"
    elif len(news_items) >= 3:
        return "medium"
    else:
        return "low"


# --------------------------------------------------
# Agent
# --------------------------------------------------
def news_narrative_agent(state):

    # 🔥 FIX 1: Use company name if available
    company = state.get("stock_name") 
    if not company:
         company = state.get("stock_symbol")

    if not company:
         raise ValueError("No valid company input")

    news_items = get_company_news(company)

    if not news_items:
        return {
            "news_narrative": {
                "sentiment": "neutral",
                "dominant_themes": [],
                "key_events": [],
                "narrative_direction": "uncertain",
                "time_horizon": "short-term",
                "confidence": "low",
                "summary": "No recent relevant news found for this company.",
                "raw_news": []
            }
        }

    result = chain.invoke({
        "company": company,
        "news_data": news_items
    })

    # 🔥 FIX 2: improved confidence
    result.confidence = compute_confidence(news_items)

    return {
        "news_narrative": {
            "sentiment": result.sentiment,
            "dominant_themes": result.dominant_themes,
            "key_events": result.key_events,
            "narrative_direction": result.narrative_direction,
            "time_horizon": result.time_horizon,
            "confidence": result.confidence,
            "summary": result.summary,
            "raw_news": news_items
        }
    }