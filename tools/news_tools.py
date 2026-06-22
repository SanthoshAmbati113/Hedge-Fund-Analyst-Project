import requests
import os
import time
from dotenv import load_dotenv
from pathlib import Path

load_dotenv(Path(__file__).resolve().parents[1] / ".env")

API_KEY = os.getenv("NEWS_API_KEY")
BASE_URL = "https://newsapi.org/v2/everything"


# --------------------------------------------------
# 🔥 Relevance Scoring (ONLY scoring, no filtering)
# --------------------------------------------------
def relevance_score(article, company):

    headline = article.get("headline") or ""
    snippet = article.get("snippet") or ""

    text = f"{headline} {snippet}".lower()
    company = (company or "").lower()

    score = 0

    # 🔥 Strong company mention
    if company in text:
        score += 3

    # 🔥 HIGH IMPACT signals
    financial_keywords = [
        "earnings", "revenue", "profit", "guidance",
        "stock", "shares", "forecast", "analyst",
        "downgrade", "upgrade", "target price"
    ]

    for k in financial_keywords:
        if k in text:
            score += 4

    return score


# --------------------------------------------------
# 🔥 Junk filter (VERY IMPORTANT)
# --------------------------------------------------
def is_relevant_article(article, company):

    headline = (article.get("headline") or "").lower()
    snippet = (article.get("snippet") or "").lower()
    text = f"{headline} {snippet}"

    company = (company or "").lower()

    # ✅ MUST contain company in headline (strict)
    if company not in headline:
        return False

    # ❌ Remove junk categories
    junk_keywords = [
        "nfl", "nba", "cricket", "pokemon", "movie",
        "celebrity", "tv show", "review", "hands-on",
        "gaming laptop", "specs", "preview", "guide"
    ]

    if any(k in text for k in junk_keywords):
        return False

    return True


# --------------------------------------------------
# 🔥 MAIN FUNCTION
# --------------------------------------------------
def get_company_news(company, max_results=10, retries=2):

    if not API_KEY:
        raise RuntimeError("NEWS_API_KEY not set")

    # 🔥 Stronger query (IMPORTANT)
    query = f'"{company}" AND (stock OR earnings OR revenue OR business OR company)'

    params = {
        "q": query,
        "language": "en",
        "sortBy": "publishedAt",
        "pageSize": 30,
        "apiKey": API_KEY
    }

    for attempt in range(retries):
        try:
            response = requests.get(BASE_URL, params=params, timeout=10)
            data = response.json()

            if data.get("status") != "ok":
                print(f"[Retry {attempt+1}] API error")
                time.sleep(1)
                continue

            articles = data.get("articles", [])

            if not articles:
                print(f"[Retry {attempt+1}] No articles found")
                time.sleep(1)
                continue

            seen_urls = set()
            scored_articles = []

            for item in articles:
                article = {
                    "headline": item.get("title"),
                    "source": item.get("source", {}).get("name"),
                    "published_at": item.get("publishedAt"),
                    "url": item.get("url"),
                    "snippet": item.get("description"),
                    "provider": "newsapi"
                }

                # ❌ Basic validation
                if not article["headline"] or not article["url"]:
                    continue

                if not article["snippet"]:
                    continue

                if article["url"] in seen_urls:
                    continue

                # 🔥 HARD FILTER (FIRST)
                if not is_relevant_article(article, company):
                    continue

                # 🔥 SCORE (SECOND)
                score = relevance_score(article, company)

                if score < 3:
                    continue

                seen_urls.add(article["url"])
                scored_articles.append((score, article))

            # 🔴 Retry if nothing useful
            if not scored_articles:
                print(f"[Retry {attempt+1}] No relevant articles after filtering")
                time.sleep(1)
                continue

            # 🔥 Sort by score
            scored_articles.sort(key=lambda x: x[0], reverse=True)

            final_articles = [a for _, a in scored_articles[:max_results]]

            return final_articles

        except Exception as e:
            print(f"[Retry {attempt+1}] Error:", e)
            time.sleep(1)

    # ❌ FINAL FAILURE
    return []