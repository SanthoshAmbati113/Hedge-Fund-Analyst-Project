from agents.news_narrative import news_narrative_agent


# ============================================================
# TEST CONFIG
# ============================================================

STOCK_SYMBOL = "AAPL"

# Optional company name for the LLM context
STOCK_NAME = "Apple"


# ============================================================
# TEST NEWS AGENT
# ============================================================

def test_news_narrative_agent():

    print("=" * 80)
    print(f"Testing News Narrative Agent for {STOCK_SYMBOL}")
    print("=" * 80)


    # --------------------------------------------------------
    # 1. Create agent state
    # --------------------------------------------------------

    state = {
        "stock_symbol": STOCK_SYMBOL,
        "stock_name": STOCK_NAME
    }


    # --------------------------------------------------------
    # 2. Invoke agent
    # --------------------------------------------------------

    result = news_narrative_agent(state)


    # --------------------------------------------------------
    # 3. Basic validation
    # --------------------------------------------------------

    assert result is not None, \
        "Agent returned None"

    assert "news_narrative" in result, \
        "Missing 'news_narrative' in agent response"


    news_narrative = result["news_narrative"]


    print("\n" + "=" * 80)
    print("NEWS NARRATIVE")
    print("=" * 80)


    # --------------------------------------------------------
    # 4. Check required output fields
    # --------------------------------------------------------

    required_fields = [
        "sentiment",
        "dominant_themes",
        "key_events",
        "narrative_direction",
        "time_horizon",
        "confidence",
        "summary",
        "raw_news"
    ]


    for field in required_fields:

        assert field in news_narrative, (
            f"Missing field: {field}"
        )


    print("✅ All required fields present")


    # --------------------------------------------------------
    # 5. Display synthesized analysis
    # --------------------------------------------------------

    print(
        f"\nSentiment:\n"
        f"{news_narrative['sentiment']}"
    )


    print(
        f"\nNarrative Direction:\n"
        f"{news_narrative['narrative_direction']}"
    )


    print(
        f"\nTime Horizon:\n"
        f"{news_narrative['time_horizon']}"
    )


    print(
        f"\nConfidence:\n"
        f"{news_narrative['confidence']}"
    )


    # --------------------------------------------------------
    # 6. Dominant themes
    # --------------------------------------------------------

    print("\n" + "-" * 80)
    print("DOMINANT THEMES")
    print("-" * 80)


    themes = news_narrative["dominant_themes"]


    assert isinstance(themes, list), \
        "dominant_themes must be a list"


    for i, theme in enumerate(
        themes,
        start=1
    ):

        print(
            f"{i}. {theme}"
        )


    # --------------------------------------------------------
    # 7. Key events
    # --------------------------------------------------------

    print("\n" + "-" * 80)
    print("KEY EVENTS")
    print("-" * 80)


    events = news_narrative["key_events"]


    assert isinstance(events, list), \
        "key_events must be a list"


    for i, event in enumerate(
        events,
        start=1
    ):

        print(
            f"{i}. {event}"
        )


    # --------------------------------------------------------
    # 8. Summary
    # --------------------------------------------------------

    print("\n" + "-" * 80)
    print("SUMMARY")
    print("-" * 80)


    summary = news_narrative["summary"]


    assert isinstance(summary, str), \
        "summary must be a string"


    assert summary.strip(), \
        "summary cannot be empty"


    print(summary)


    # --------------------------------------------------------
    # 9. Raw news
    # --------------------------------------------------------

    raw_news = news_narrative["raw_news"]


    assert isinstance(raw_news, list), \
        "raw_news must be a list"


    print("\n" + "-" * 80)
    print(
        f"RAW ARTICLES RETRIEVED: {len(raw_news)}"
    )
    print("-" * 80)


    # --------------------------------------------------------
    # 10. Display every article
    # --------------------------------------------------------

    for i, article in enumerate(
        raw_news,
        start=1
    ):

        print("\n" + "." * 80)

        print(
            f"ARTICLE {i}"
        )

        print(
            f"Headline : "
            f"{article.get('headline')}"
        )

        print(
            f"Source   : "
            f"{article.get('source')}"
        )

        print(
            f"Published: "
            f"{article.get('published_at')}"
        )

        print(
            f"Sentiment: "
            f"{article.get('overall_sentiment_label')}"
        )

        print(
            f"Score    : "
            f"{article.get('overall_sentiment_score')}"
        )

        print(
            f"URL      : "
            f"{article.get('url')}"
        )


    # --------------------------------------------------------
    # 11. Validate article structure
    # --------------------------------------------------------

    required_article_fields = [
        "headline",
        "source",
        "published_at",
        "url",
        "summary",
        "overall_sentiment_score",
        "overall_sentiment_label",
        "provider"
    ]


    for i, article in enumerate(
        raw_news,
        start=1
    ):

        for field in required_article_fields:

            assert field in article, (
                f"Article {i} missing field: {field}"
            )


    print(
        "\n✅ All raw articles contain required fields"
    )


    # --------------------------------------------------------
    # 12. Validate provider
    # --------------------------------------------------------

    providers = {
        article["provider"]
        for article in raw_news
    }


    assert providers == {
        "alpha_vantage"
    }


    print(
        "✅ All articles came from Alpha Vantage"
    )


    # --------------------------------------------------------
    # FINAL
    # --------------------------------------------------------

    print("\n" + "=" * 80)
    print("✅ NEWS NARRATIVE AGENT TEST PASSED")
    print("=" * 80)


# ============================================================
# RUN DIRECTLY
# ============================================================

if __name__ == "__main__":

    test_news_narrative_agent()