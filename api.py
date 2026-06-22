from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn
import traceback

from graph.workflow import build_graph


# --------------------------------------------------
# FastAPI App
# --------------------------------------------------
app = FastAPI(
    title="Hedge Fund AI Analyst API",
    description="Multi-Agent Financial Intelligence System",
    version="1.0.0"
)


# --------------------------------------------------
# CORS (IMPORTANT for Streamlit frontend)
# --------------------------------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# --------------------------------------------------
# Build LangGraph App Once
# --------------------------------------------------
graph_app = build_graph()


# --------------------------------------------------
# Request Schema
# --------------------------------------------------
class StockRequest(BaseModel):
    stock_name: str


# --------------------------------------------------
# Health Route
# --------------------------------------------------
@app.get("/")
def health_check():
    return {
        "status": "running",
        "service": "Hedge Fund AI Analyst API"
    }


# --------------------------------------------------
# Main Analysis Route
# --------------------------------------------------
@app.post("/analyze")
def analyze_stock(request: StockRequest):

    stock = request.stock_name.strip()

    if not stock:
        raise HTTPException(status_code=400, detail="Stock name cannot be empty")

    # Initial graph state
    initial_state = {
        "stock_name": stock,

        # populated later
        "stock_symbol": "",

        "market_intelligence": {},
        "fundamental_analysis": {},
        "news_narrative": {},
        "risk_scenario": {},
        "final_thesis": {}
    }
    
    try:
        final_state = graph_app.invoke(initial_state)

        return {
            "success": True,
            "stock_name": stock,
            "stock_symbol": final_state.get("stock_symbol"),
            "market_intelligence": final_state.get("market_intelligence"),
            "fundamental_analysis": final_state.get("fundamental_analysis"),
            "news_narrative": final_state.get("news_narrative"),
            "risk_scenario": final_state.get("risk_scenario"),
            "final_thesis": final_state.get("final_thesis")
        }

    

    except Exception as e:
        print("\n===== FULL ERROR TRACEBACK =====")
        traceback.print_exc()

        raise HTTPException(
          status_code=500,
           detail=str(e)
    )
    
if __name__ == "__main__":
    uvicorn.run(
        "api:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )      