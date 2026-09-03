from langgraph.graph import StateGraph, END
from graph.state import HFState

from agents.symbol_resolver import resolve_symbol_agent

from agents.market_intelligence import market_intelligence_agent
from agents.fundamental_analysis import fundamentals_agent
from agents.news_narrative import news_narrative_agent
from agents.risk_assesment import risk_assessment_agent
from agents.thesis_synthesis import thesis_synthesis_agent


# ============================================================
# AGENT WRAPPER
# ============================================================

def run_agent(agent, agent_name):

    def wrapped_agent(state):

        print(f"\n[▶] Running {agent_name}...")

        try:

            result = agent(state)

            print(f"[✓] {agent_name} completed successfully")

            return result

        except Exception as e:

            print(f"[✗] {agent_name} failed: {e}")

            raise

    return wrapped_agent


# ============================================================
# BUILD GRAPH
# ============================================================

def build_graph():

    graph = StateGraph(HFState)

    # --------------------------------------------------------
    # Nodes
    # --------------------------------------------------------

    graph.add_node(
        "resolve_symbol",
        run_agent(
            resolve_symbol_agent,
            "Symbol Resolver"
        )
    )

    graph.add_node(
        "market_intelligence",
        run_agent(
            market_intelligence_agent,
            "Market Intelligence"
        )
    )

    graph.add_node(
        "fundamental_analysis",
        run_agent(
            fundamentals_agent,
            "Fundamental Analysis"
        )
    )

    graph.add_node(
        "news_narrative",
        run_agent(
            news_narrative_agent,
            "News Narrative"
        )
    )

    graph.add_node(
        "risk_scenario",
        run_agent(
            risk_assessment_agent,
            "Risk Assessment"
        )
    )

    graph.add_node(
        "thesis_synthesis",
        run_agent(
            thesis_synthesis_agent,
            "Thesis Synthesis"
        )
    )

    # --------------------------------------------------------
    # Entry
    # --------------------------------------------------------

    graph.set_entry_point("resolve_symbol")

    # --------------------------------------------------------
    # PARALLEL FAN-OUT
    # --------------------------------------------------------

    graph.add_edge(
        "resolve_symbol",
        "market_intelligence"
    )

    graph.add_edge(
        "resolve_symbol",
        "fundamental_analysis"
    )

    graph.add_edge(
        "resolve_symbol",
        "news_narrative"
    )

    # --------------------------------------------------------
    # FAN-IN → RISK
    # --------------------------------------------------------

    graph.add_edge(
        "market_intelligence",
        "risk_scenario"
    )

    graph.add_edge(
        "fundamental_analysis",
        "risk_scenario"
    )

    graph.add_edge(
        "news_narrative",
        "risk_scenario"
    )

    # --------------------------------------------------------
    # FINAL SYNTHESIS
    # --------------------------------------------------------

    graph.add_edge(
        "risk_scenario",
        "thesis_synthesis"
    )

    graph.add_edge(
        "thesis_synthesis",
        END
    )

    return graph.compile()