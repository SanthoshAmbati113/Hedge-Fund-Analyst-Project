from agents.news_narrative import news_narrative_agent


def run_test():
    # Fake LangGraph state
    state = {
        "stock_name": "tesla"
    }

    print("\n=== News & Narrative Agent Test ===")
    print(f"Company: {state['stock_name']}")
    print("-" * 60)

    result = news_narrative_agent(state)

    narrative = result.get("news_narrative", {})

    print("\n--- Sentiment ---")
    print(narrative.get("sentiment"))

    print("\n--- Narrative Direction ---")
    print(narrative.get("narrative_direction"))

    print("\n--- Dominant Themes ---")
    for t in narrative.get("dominant_themes", []):
        print("-", t)

    print("\n--- Key Events ---")
    for e in narrative.get("key_events", []):
        print("-", e)

    print("\n--- Time Horizon ---")
    print(narrative.get("time_horizon"))

    print("\n--- Confidence ---")
    print(narrative.get("confidence"))

    print("\n--- Summary ---")
    print(narrative.get("summary"))

    print("\n--- Articles Fetched ---")
    print(len(narrative.get("raw_news", [])))


if __name__ == "__main__":
    run_test()
