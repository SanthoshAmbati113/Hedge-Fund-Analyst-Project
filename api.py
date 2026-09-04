import observability  # noqa: F401  # must be imported before langgraph/langchain

import traceback

import logfire
import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from observability import configure_logfire, instrument_fastapi_app
from graph.workflow import build_graph


# ============================================================
# FASTAPI APP
# ============================================================

app = FastAPI(
    title="Hedge Fund AI Analyst API",
    description=(
        "Multi-Agent Financial Intelligence System "
        "for Market, Fundamental, News, Risk and Thesis Analysis"
    ),
    version="2.0.0"
)

configure_logfire(service_name="hedge-fund-analyst-api")
instrument_fastapi_app(app)


# ============================================================
# CORS
# ============================================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================================
# BUILD LANGGRAPH APP
# ============================================================

# Build once when the API starts.
# We don't rebuild the graph for every request.
graph_app = build_graph()


# ============================================================
# REQUEST SCHEMA
# ============================================================

class StockRequest(BaseModel):
    stock_name: str


# ============================================================
# HEALTH CHECK
# ============================================================

@app.get("/")
def health_check():

    return {
        "status": "running",
        "service": "Hedge Fund AI Analyst API",
        "version": "2.0.0"
    }


# ============================================================
# ANALYSIS ROUTE
# ============================================================

@app.post("/analyze")
def analyze_stock(request: StockRequest):

    # --------------------------------------------------------
    # Validate input
    # --------------------------------------------------------

    stock = request.stock_name.strip()

    if not stock:

        raise HTTPException(
            status_code=400,
            detail="Stock name or symbol cannot be empty"
        )


    # --------------------------------------------------------
    # Initial LangGraph State
    # --------------------------------------------------------

    initial_state = {

        # User input
        "stock_name": stock,

        # Symbol will be resolved by the graph
        "stock_symbol": "",

        # Agent outputs
        "market_intelligence": {},
        "fundamental_analysis": {},
        "news_narrative": {},
        "risk_scenario": {},
        "final_thesis": {}
    }


    # --------------------------------------------------------
    # Execute Multi-Agent Workflow
    # --------------------------------------------------------

    try:

        with logfire.span(
            "analyze_stock",
            stock_name=stock,
            workflow="hedge_fund_analysis",
        ):
            final_state = graph_app.invoke(
                initial_state
            )


        # ----------------------------------------------------
        # Extract final results
        # ----------------------------------------------------

        stock_symbol = final_state.get(
            "stock_symbol",
            ""
        )

        market_intelligence = final_state.get(
            "market_intelligence",
            {}
        )

        fundamental_analysis = final_state.get(
            "fundamental_analysis",
            {}
        )

        news_narrative = final_state.get(
            "news_narrative",
            {}
        )

        risk_scenario = final_state.get(
            "risk_scenario",
            {}
        )

        final_thesis = final_state.get(
            "final_thesis",
            {}
        )


        # ----------------------------------------------------
        # Final API Response
        # ----------------------------------------------------

        return {

            "success": True,

            "stock_name": stock,

            "stock_symbol": stock_symbol,

            # ----------------------------------------------
            # Individual Agent Outputs
            # ----------------------------------------------

            "market_intelligence":
                market_intelligence,

            "fundamental_analysis":
                fundamental_analysis,

            "news_narrative":
                news_narrative,

            "risk_scenario":
                risk_scenario,

            # ----------------------------------------------
            # Final Investment Thesis
            # ----------------------------------------------

            "final_thesis":
                final_thesis
        }


    # --------------------------------------------------------
    # Error Handling
    # --------------------------------------------------------

    except Exception as e:

        logfire.exception(
            "analysis pipeline failed",
            stock_name=stock,
            error_type=type(e).__name__,
        )

        print(
            "\n===== FULL ERROR TRACEBACK ====="
        )

        traceback.print_exc()


        raise HTTPException(
            status_code=500,
            detail={
                "error": "Analysis pipeline failed",
                "message": str(e)
            }
        )


# ============================================================
# RUN SERVER
# ============================================================

if __name__ == "__main__":

    uvicorn.run(
        "api:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )