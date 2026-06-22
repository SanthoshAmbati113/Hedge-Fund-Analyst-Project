from agents.risk_assesment import risk_assessment_agent


def run_test():
    print("\n=== RISK AGENT TEST ===\n")

    # --------------------------------------------------
    # SAMPLE STATE (REALISTIC)
    # --------------------------------------------------
    state = {
        "market_intelligence": {
            "stock": "AAPL",
            "analysis": "The stock is in a mild uptrend with moderate volatility. Momentum remains positive but shows signs of short-term consolidation.",
            "raw_data": {
                "price": 190,
                "trend": "uptrend",
                "volatility": "moderate"
            }
        },

        "fundamental_analysis": {
            "signals": {
                "profitability": "strong",
                "financial_health": "strong",
                "valuation": "slightly expensive",
                "growth": "moderate",
                "cash_flow_quality": "strong",
                "overall_strength": "strong",
                "confidence": "high"
            },
            "summary": "Strong balance sheet and profitability with slightly elevated valuation.",
            "raw_data": {}
        },

        "news_narrative": {
            "sentiment": "slightly positive",
            "dominant_themes": [
                "earnings growth",
                "AI-driven product expansion"
            ],
            "key_events": [
                "Strong earnings expectations",
                "AI features rollout"
            ],
            "narrative_direction": "improving",
            "time_horizon": "short-term",
            "confidence": "medium",
            "summary": "Narrative is driven by earnings expectations and innovation."
        }
    }

    # --------------------------------------------------
    # RUN AGENT
    # --------------------------------------------------
    result = risk_assessment_agent(state)

    # --------------------------------------------------
    # PRINT OUTPUT CLEANLY
    # --------------------------------------------------
    print("RISK OUTPUT:\n")
    for key, value in result["risk_scenario"].items():
        print(f"{key}: {value}")


# --------------------------------------------------
# RUN
# --------------------------------------------------
if __name__ == "__main__":
    run_test()