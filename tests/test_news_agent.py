from agents.news_narrative import news_narrative_agent

def run():
    # You can switch this between ticker / company name
    state = {
        "stock_symbol": "NVDA",      # or "TSLA", "GOOGL"
        "stock_name": "NVIDIA"      # improves NewsAPI relevance
    }

    result = news_narrative_agent(state)

    print("\n=== NEWS AGENT TEST ===")
    print("=" * 60)

    na = result["news_narrative"]

    print("\n--- SIGNALS ---")
    print("Sentiment:", na["sentiment"])
    print("Narrative Direction:", na["narrative_direction"])
    print("Time Horizon:", na["time_horizon"])
    print("Confidence:", na["confidence"])

    print("\n--- DOMINANT THEMES ---")
    for t in na["dominant_themes"]:
        print(" -", t)

    print("\n--- KEY EVENTS ---")
    for e in na["key_events"]:
        print(" -", e)

    print("\n--- SUMMARY ---")
    print(na["summary"])

    print("\n--- RAW NEWS INFO ---")
    raw = na.get("raw_news", [])
    print(f"Total articles used: {len(raw)}")

    for i, article in enumerate(raw[:5], 1):  # show first 5
        print(f"\n{i}. {article['headline']}")
        print("   Source:", article["source"])
        print("   Date:", article["published_at"])


if __name__ == "__main__":
    run()