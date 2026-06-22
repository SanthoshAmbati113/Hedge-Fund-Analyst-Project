from langgraph.graph import StateGraph,START,END
from langgraph.graph  import MessagesState
from typing import Dict,Any
from pydantic import Field

class HFState(MessagesState):
    stock_name: str = ""
    stock_symbol: str = ""

    market_intelligence: Dict[str, Any] = Field(default_factory=dict)
    fundamental_analysis: Dict[str, Any] = Field(default_factory=dict)
    news_narrative: Dict[str, Any] = Field(default_factory=dict)
    risk_scenario: Dict[str, Any] = Field(default_factory=dict)

    final_thesis: Dict[str, Any] = {}
    next_agent: str = ""
    
    
   

