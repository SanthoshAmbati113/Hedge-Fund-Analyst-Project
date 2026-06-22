import requests
import os
import time

API_KEY = os.getenv("ALPHA_VANTAGE_API_KEY")


def resolve_symbol_agent(state):
    # 🔹 Read user input (standardize on stock_name)
    user_input = state.get("stock_name", "").strip()

    if not user_input:
        raise ValueError("Stock input is empty")

    # 🔹 If already looks like a ticker
    if user_input.isupper() and 1 <= len(user_input) <= 5:
        return {"stock_symbol": user_input}

    # 🔹 Alpha Vantage search
    url = "https://www.alphavantage.co/query"
    params = {
        "function": "SYMBOL_SEARCH",
        "keywords": user_input,
        "apikey": API_KEY
    }

    matches = []

    # 🔁 single retry (2 attempts total)
    for attempt in range(2):
        try:
            res = requests.get(url, params=params, timeout=10)
            data = res.json()

            matches = data.get("bestMatches", [])
            if matches:
                break

        except Exception:
            pass

        time.sleep(1)

    if not matches:
        raise ValueError(f"No stock symbol found for: {user_input}")

    # 🔹 Prefer US equities
    PREFERRED_REGION = "United States"
    for m in matches:
        if m.get("4. region") == PREFERRED_REGION:
            return {"stock_symbol": m.get("1. symbol").upper()}

    # 🔹 fallback → first match
    return {
        "stock_symbol": matches[0].get("1. symbol").upper()
    }