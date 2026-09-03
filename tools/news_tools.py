import requests
import os
import time
from dotenv import load_dotenv
from pathlib import Path


# ============================================================
# ENVIRONMENT
# ============================================================

load_dotenv(
    Path(__file__).resolve().parents[1] / ".env"
)

API_KEY = os.getenv("ALPHA_VANTAGE_API_KEY")

BASE_URL = "https://www.alphavantage.co/query"


# ============================================================
# THROTTLE
# ============================================================

LAST_CALL = 0


def throttle():

    global LAST_CALL

    now = time.time()

    # Alpha Vantage: approximately 5 calls/minute
    if now - LAST_CALL < 12:

        time.sleep(
            12 - (now - LAST_CALL)
        )

    LAST_CALL = time.time()


# ============================================================
# RELEVANCE SCORING
# ============================================================

def relevance_score(article, symbol):

    score = 0

    title = (
        article.get("headline") or ""
    ).lower()

    summary = (
        article.get("summary") or ""
    ).lower()

    text = f"{title} {summary}"

    symbol = (
        symbol or ""
    ).lower()


    # --------------------------------------------------------
    # Ticker/company relevance
    # --------------------------------------------------------

    if symbol in text:
        score += 5


    # --------------------------------------------------------
    # High-impact financial events
    # --------------------------------------------------------

    high_impact_keywords = [

        "earnings",
        "revenue",
        "profit",
        "loss",
        "guidance",
        "forecast",

        "acquisition",
        "merger",
        "takeover",

        "ipo",

        "upgrade",
        "downgrade",
        "price target",
        "analyst",

        "regulation",
        "lawsuit",
        "investigation",

        "ceo",
        "management",

        "dividend",
        "buyback",

        "product launch",
        "partnership",

        "bankruptcy",
        "recall"
    ]


    for keyword in high_impact_keywords:

        if keyword in text:
            score += 3


    return score


# ============================================================
# BASIC ARTICLE VALIDATION
# ============================================================

def is_valid_article(article):

    headline = article.get("headline")
    url = article.get("url")
    summary = article.get("summary")

    if not headline:
        return False

    if not url:
        return False

    if not summary:
        return False

    return True


# ============================================================
# FETCH ALPHA VANTAGE NEWS
# ============================================================

def fetch_news(symbol, limit=30):

    if not API_KEY:

        raise RuntimeError(
            "ALPHA_VANTAGE_API_KEY not set"
        )


    throttle()


    params = {

        "function": "NEWS_SENTIMENT",

        "tickers": symbol,

        "sort": "LATEST",

        "limit": limit,

        "apikey": API_KEY
    }


    response = requests.get(
        BASE_URL,
        params=params,
        timeout=10
    )


    response.raise_for_status()

    return response.json()


# ============================================================
# MAIN FUNCTION
# ============================================================

def get_company_news(
    symbol,
    max_results=15,
    candidate_limit=30
):

    """
    Fetch recent company-specific news from Alpha Vantage.

    Flow:

        Alpha Vantage NEWS_SENTIMENT
                ↓
        ticker-filtered articles
                ↓
        basic validation
                ↓
        relevance scoring
                ↓
        top N articles
    """

    try:

        # ====================================================
        # API CALL
        # ====================================================

        data = fetch_news(
            symbol,
            candidate_limit
        )


        # ====================================================
        # API LIMIT / ERROR HANDLING
        # ====================================================

        if "Information" in data:

            print(
                "Alpha Vantage API information:",
                data["Information"]
            )

            return []


        if "Note" in data:

            print(
                "Alpha Vantage API limit:",
                data["Note"]
            )

            return []


        # ====================================================
        # RAW FEED
        # ====================================================

        feed = data.get(
            "feed",
            []
        )


        if not feed:

            print(
                f"No news found for {symbol}"
            )

            return []


        # ====================================================
        # PROCESS ARTICLES
        # ====================================================

        seen_urls = set()

        scored_articles = []


        for item in feed:

            # ------------------------------------------------
            # Alpha Vantage article structure
            # ------------------------------------------------

            article = {

                "headline":
                    item.get("title"),

                "source":
                    item.get("source"),

                "published_at":
                    item.get("time_published"),

                "url":
                    item.get("url"),

                "summary":
                    item.get("summary"),

                "overall_sentiment_score":
                    item.get(
                        "overall_sentiment_score"
                    ),

                "overall_sentiment_label":
                    item.get(
                        "overall_sentiment_label"
                    ),

                "provider":
                    "alpha_vantage"
            }


            # ------------------------------------------------
            # Basic validation
            # ------------------------------------------------

            if not is_valid_article(
                article
            ):
                continue


            # ------------------------------------------------
            # Remove duplicates
            # ------------------------------------------------

            if article["url"] in seen_urls:

                continue


            # ------------------------------------------------
            # Relevance score
            # ------------------------------------------------

            score = relevance_score(
                article,
                symbol
            )


            seen_urls.add(
                article["url"]
            )


            scored_articles.append(
                (
                    score,
                    article
                )
            )


        # ====================================================
        # NO VALID ARTICLES
        # ====================================================

        if not scored_articles:

            return []


        # ====================================================
        # SORT BY RELEVANCE
        # ====================================================

        scored_articles.sort(
            key=lambda x: x[0],
            reverse=True
        )


        # ====================================================
        # RETURN TOP ARTICLES
        # ====================================================

        final_articles = [

            article

            for _, article
            in scored_articles[
                :max_results
            ]

        ]


        return final_articles


    except requests.exceptions.RequestException as e:

        print(
            "News API request error:",
            e
        )

        return []


    except Exception as e:

        print(
            "News processing error:",
            e
        )

        return []