from tools.news_tools import get_company_news


# ============================================================
# TEST CONFIG
# ============================================================

SYMBOL = "AAPL"
MAX_RESULTS = 15


# ============================================================
# TEST NEWS TOOL
# ============================================================

def test_get_company_news():

    print("=" * 70)
    print(f"Testing News Tool for: {SYMBOL}")
    print("=" * 70)

    articles = get_company_news(
        symbol=SYMBOL,
        max_results=MAX_RESULTS,
        candidate_limit=30
    )

    # --------------------------------------------------------
    # 1. Check API returned something
    # --------------------------------------------------------

    assert articles is not None, \
        "News tool returned None"

    print(
        f"\nArticles returned: {len(articles)}"
    )

    if not articles:

        print(
            "\n❌ No articles returned."
        )

        return


    # --------------------------------------------------------
    # 2. Check result limit
    # --------------------------------------------------------

    assert len(articles) <= MAX_RESULTS, (
        f"Returned {len(articles)} articles, "
        f"expected at most {MAX_RESULTS}"
    )

    print(
        f"✅ Result count <= {MAX_RESULTS}"
    )


    # --------------------------------------------------------
    # 3. Required fields
    # --------------------------------------------------------

    required_fields = [
        "headline",
        "source",
        "published_at",
        "url",
        "summary",
        "overall_sentiment_score",
        "overall_sentiment_label",
        "provider"
    ]


    # --------------------------------------------------------
    # 4. Validate every article
    # --------------------------------------------------------

    for i, article in enumerate(
        articles,
        start=1
    ):

        print("\n" + "-" * 70)
        print(f"ARTICLE {i}")
        print("-" * 70)

        # ---------------------------------------------
        # Required fields
        # ---------------------------------------------

        for field in required_fields:

            assert field in article, (
                f"Article {i} missing field: {field}"
            )

        print(
            f"Headline : {article['headline']}"
        )

        print(
            f"Source   : {article['source']}"
        )

        print(
            f"Published: {article['published_at']}"
        )

        print(
            f"Sentiment: "
            f"{article['overall_sentiment_label']}"
        )

        print(
            f"Score    : "
            f"{article['overall_sentiment_score']}"
        )

        print(
            f"URL      : {article['url']}"
        )

        print(
            f"Provider : {article['provider']}"
        )


    # --------------------------------------------------------
    # 5. Check provider
    # --------------------------------------------------------

    providers = {
        article["provider"]
        for article in articles
    }

    assert providers == {
        "alpha_vantage"
    }

    print(
        "\n✅ Provider correctly identified as Alpha Vantage"
    )


    # --------------------------------------------------------
    # 6. Check URLs are unique
    # --------------------------------------------------------

    urls = [
        article["url"]
        for article in articles
    ]

    assert len(urls) == len(set(urls)), (
        "Duplicate article URLs found"
    )

    print(
        "✅ No duplicate articles"
    )


    # --------------------------------------------------------
    # FINAL
    # --------------------------------------------------------

    print("\n" + "=" * 70)
    print("✅ NEWS TOOL TEST PASSED")
    print("=" * 70)


# ============================================================
# RUN DIRECTLY
# ============================================================

if __name__ == "__main__":

    test_get_company_news()