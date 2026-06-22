from langchain_groq import ChatGroq
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import PydanticOutputParser
from dotenv import load_dotenv
from pathlib import Path

from hf_schemas.thesis_schema import InvestmentThesis

load_dotenv(Path(__file__).resolve().parents[1] / ".env")

# --------------------------------------------------
# LLM
# --------------------------------------------------
llm = ChatGroq(
    model="llama-3.1-8b-instant",
    temperature=0
)

parser = PydanticOutputParser(pydantic_object=InvestmentThesis)

# --------------------------------------------------
# Prompt
# --------------------------------------------------
prompt_path = Path(__file__).resolve().parents[1] / "prompts" / "thesis_synthesis.txt"
with open(prompt_path, "r", encoding="utf-8") as f:
    prompt_text = f.read()

prompt = PromptTemplate(
    template=prompt_text,
    input_variables=[
        "market_intelligence",
        "fundamentals",
        "news_narrative",
        "risk_analysis"
    ],
    partial_variables={
        "format_instruction": parser.get_format_instructions()
    }
)

chain = prompt | llm | parser

# --------------------------------------------------
# Helper: Human-readable renderer
# --------------------------------------------------
def render_thesis(thesis: dict) -> str:
    def render_cases(cases):
        if not cases:
            return "—"
        blocks = []
        for c in cases:
            blocks.append(
                f"• {c['title']}\n"
                f"  {c['explanation']}\n"
                f"  Evidence:\n"
                + "\n".join([f"    - {e}" for e in c.get("evidence", [])])
            )
        return "\n\n".join(blocks)

    return f"""
============================================================
FINAL INVESTMENT THESIS — {thesis['stock_symbol']}
============================================================

RECOMMENDATION
------------------------------------------------------------
View        : {thesis['recommendation'].upper()}
Conviction  : {thesis['conviction'].capitalize()}

------------------------------------------------------------
BULL CASE
------------------------------------------------------------
{render_cases(thesis.get('bull_case'))}

------------------------------------------------------------
BEAR CASE
------------------------------------------------------------
{render_cases(thesis.get('bear_case'))}

------------------------------------------------------------
VALUATION VIEW
------------------------------------------------------------
{thesis.get('valuation_view')}

------------------------------------------------------------
RISK–REWARD ASSESSMENT
------------------------------------------------------------
{thesis.get('risk_reward_summary')}

------------------------------------------------------------
FINAL SUMMARY
------------------------------------------------------------
{thesis.get('final_summary')}
""".strip()

# --------------------------------------------------
# Agent
# --------------------------------------------------
def thesis_synthesis_agent(state):

    result = chain.invoke({
        "market_intelligence": state["market_intelligence"],
        "fundamentals": state["fundamental_analysis"],
        "news_narrative": state["news_narrative"],
        "risk_analysis": state["risk_scenario"]
    })

    # 🔥 Inject risk fields explicitly into final output
    thesis = result.dict()

    thesis["risk_level"] = state["risk_scenario"].get("risk_level")
    thesis["risk_score"] = state["risk_scenario"].get("overall_risk_score")

    return {
        "final_thesis": thesis
    }