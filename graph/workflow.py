from langgraph.graph import StateGraph, END
from graph.state import HFState

from agents.symbol_resolver import resolve_symbol_agent

from agents.market_intelligence import market_intelligence_agent
from agents.fundamental_analysis import fundamentals_agent
from agents.news_narrative import news_narrative_agent
from agents.risk_assesment import risk_assessment_agent
from agents.thesis_synthesis import thesis_synthesis_agent


def build_graph():
    graph = StateGraph(HFState)

    # -----------------------------
    # Nodes
    # -----------------------------
    graph.add_node("resolve_symbol", resolve_symbol_agent)

    graph.add_node("market_intelligence", market_intelligence_agent)
    graph.add_node("fundamental_analysis", fundamentals_agent)
    graph.add_node("news_narrative", news_narrative_agent)

    graph.add_node("risk_scenario", risk_assessment_agent)
    graph.add_node("thesis_synthesis", thesis_synthesis_agent)

    # -----------------------------
    # Entry
    # -----------------------------
    graph.set_entry_point("resolve_symbol")

    # -----------------------------
    # 🔥 PARALLEL FAN-OUT
    # -----------------------------
    graph.add_edge("resolve_symbol", "market_intelligence")
    graph.add_edge("resolve_symbol", "fundamental_analysis")
    graph.add_edge("resolve_symbol", "news_narrative")

    # -----------------------------
    # 🔥 FAN-IN → risk
    # (waits for all three implicitly)
    # -----------------------------
    graph.add_edge("market_intelligence", "risk_scenario")
    graph.add_edge("fundamental_analysis", "risk_scenario")
    graph.add_edge("news_narrative", "risk_scenario")

    # -----------------------------
    # Final synthesis
    # -----------------------------
    graph.add_edge("risk_scenario", "thesis_synthesis")
    graph.add_edge("thesis_synthesis", END)

    return graph.compile()