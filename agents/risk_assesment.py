from hf_schemas.risk_schema import RiskAssessment

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
# Parser
# --------------------------------------------------
parser = PydanticOutputParser(pydantic_object=RiskAssessment)

# --------------------------------------------------
# Load Prompt
# --------------------------------------------------
prompt_path = Path(__file__).resolve().parents[1] / "prompts" / "risk_assessment.txt"

with open(prompt_path, "r", encoding="utf-8") as f:
    prompt_text = f.read()

# --------------------------------------------------
# Prompt Template
# --------------------------------------------------
template = PromptTemplate(
    template=prompt_text,
    input_variables=[
        "market_intelligence",
        "fundamentals",
        "news_narrative"
    ],
    partial_variables={
        "format_instruction": parser.get_format_instructions()
    }
)

chain = template | llm | parser


# --------------------------------------------------
# 🔥 AGENT
# --------------------------------------------------
def risk_assessment_agent(state):
    """
    Risk Agent:
    - Combines all signals
    - Produces risk scenarios
    """

    result = chain.invoke({
        "market_intelligence": state["market_intelligence"],
        "fundamentals": state["fundamental_analysis"],
        "news_narrative": state["news_narrative"]
    })

    return {
        "risk_scenario": result.dict()
    }