from langchain_groq import ChatGroq
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import PydanticOutputParser

from dotenv import load_dotenv
from pathlib import Path

from hf_schemas.thesis_schema import InvestmentThesis


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
# OUTPUT PARSER
# ============================================================

parser = PydanticOutputParser(
    pydantic_object=InvestmentThesis
)


# ============================================================
# LOAD PROMPT
# ============================================================

prompt_path = (
    Path(__file__).resolve().parents[1]
    / "prompts"
    / "thesis_synthesis.txt"
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

prompt = PromptTemplate(

    template=prompt_text,

    input_variables=[
        "market_intelligence",
        "fundamentals",
        "news_narrative",
        "risk_analysis"
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
    prompt
    | llm
    | parser
)


# ============================================================
# AGENT
# ============================================================

def thesis_synthesis_agent(state):
    """
    Final Thesis Agent.

    Synthesizes:

        Market Intelligence
        Fundamental Analysis
        News Narrative
        Risk Assessment

    into a final investment thesis.
    """

    # --------------------------------------------------------
    # Validate required inputs
    # --------------------------------------------------------

    market_intelligence = state.get(
        "market_intelligence"
    )

    fundamentals = state.get(
        "fundamental_analysis"
    )

    news_narrative = state.get(
        "news_narrative"
    )

    risk_analysis = state.get(
        "risk_scenario"
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


    if risk_analysis is None:
        raise ValueError(
            "Risk assessment is missing"
        )


    # --------------------------------------------------------
    # Final synthesis
    # --------------------------------------------------------

    result = chain.invoke({

        "market_intelligence":
            market_intelligence,

        "fundamentals":
            fundamentals,

        "news_narrative":
            news_narrative,

        "risk_analysis":
            risk_analysis
    })


    # --------------------------------------------------------
    # Return final thesis
    # --------------------------------------------------------

    return {
        "final_thesis":
            result.model_dump()
    }