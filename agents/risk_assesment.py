from hf_schemas.risk_schema import RiskAssessment

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
# PARSER
# ============================================================

parser = PydanticOutputParser(
    pydantic_object=RiskAssessment
)


# ============================================================
# LOAD PROMPT
# ============================================================

prompt_path = (
    Path(__file__).resolve().parents[1]
    / "prompts"
    / "risk_assessment.txt"
)


with open(
    prompt_path,
    "r",
    encoding="utf-8"
) as f:

    prompt_text = f.read()


# ============================================================
# PROMPT TEMPLATE
# ============================================================

template = PromptTemplate(

    template=prompt_text,

    input_variables=[
        "market_intelligence",
        "fundamentals",
        "news_narrative"
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
# AGENT
# ============================================================

def risk_assessment_agent(state):

    """
    Risk Assessment Agent

    Inputs:
        - market_intelligence
        - fundamental_analysis
        - news_narrative

    Output:
        - integrated risk assessment
        - risk score
        - key risks
        - key drivers
        - bull scenario
        - bear scenario
        - confidence
        - summary
    """

    # ========================================================
    # 1. VALIDATE INPUTS
    # ========================================================

    market_intelligence = state.get(
        "market_intelligence"
    )

    fundamentals = state.get(
        "fundamental_analysis"
    )

    news_narrative = state.get(
        "news_narrative"
    )


    if market_intelligence is None:

        raise ValueError(
            "Market intelligence is missing"
        )


    if fundamentals is None:

        raise ValueError(
            "Fundamental analysis is missing"
        )


    if news_narrative is None:

        raise ValueError(
            "News narrative is missing"
        )


    # ========================================================
    # 2. RUN RISK ANALYSIS
    # ========================================================

    result = chain.invoke({

        "market_intelligence":
            market_intelligence,

        "fundamentals":
            fundamentals,

        "news_narrative":
            news_narrative
    })


    # ========================================================
    # 3. RETURN STRUCTURED RESULT
    # ========================================================

    return {

        "risk_scenario":
            result.model_dump()
    }