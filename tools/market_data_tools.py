import requests
import os
import time
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("ALPHA_VANTAGE_API_KEY")
BASE_URL = "https://www.alphavantage.co/query"

# -----------------------------
# Throttle (IMPORTANT)
# -----------------------------
LAST_CALL = 0

def throttle():
    global LAST_CALL
    now = time.time()

    # Alpha Vantage: ~5 calls/min → 12 sec gap
    if now - LAST_CALL < 12:
        time.sleep(12 - (now - LAST_CALL))

    LAST_CALL = time.time()


# -----------------------------
# FETCH QUOTE
# -----------------------------
def fetch_quote(symbol):
    throttle()

    params = {
        "function": "GLOBAL_QUOTE",
        "symbol": symbol,
        "apikey": API_KEY
    }

    res = requests.get(BASE_URL, params=params, timeout=10)
    data = res.json()

    return data  # ✅ return full response (important)


# -----------------------------
# FETCH DAILY (OPTIONAL)
# -----------------------------
def fetch_daily(symbol):
    throttle()

    params = {
        "function": "TIME_SERIES_DAILY",
        "symbol": symbol,
        "apikey": API_KEY
    }

    res = requests.get(BASE_URL, params=params, timeout=10)
    data = res.json()

    return data.get("Time Series (Daily)", {})


# -----------------------------
# METRICS
# -----------------------------
def compute_metrics(daily_data):
    try:
        dates = list(daily_data.keys())
        closes = [float(daily_data[d]["4. close"]) for d in dates[:30]]

        latest = closes[0]
        prev = closes[1]

        return {
            "trend": "uptrend" if latest > closes[-1] else "downtrend",
            "volatility": max(closes) - min(closes),
            "momentum": "positive" if latest > prev else "negative"
        }

    except Exception:
        return {
            "trend": "unknown",
            "volatility": None,
            "momentum": "unknown"
        }


# -----------------------------
# MAIN FUNCTION
# -----------------------------
def get_market_data(symbol, retries=2):
    """
    Clean + reliable market data fetch
    """

    for attempt in range(retries):
        try:
            quote_raw = fetch_quote(symbol)

            # =============================
            # 🔴 HANDLE API LIMIT / BAD RESPONSE
            # =============================
            if not quote_raw or not isinstance(quote_raw, dict):
                return {
                            "error": "invalid_response",
                            "symbol": symbol,
                            "confidence": "low"
                       }

            # Alpha Vantage rate limit / notice handling
            if "Information" in quote_raw or "Note" in quote_raw:  
                    return {
                              "error": "api_limit_or_throttle",
                              "symbol": symbol,
                              "confidence": "low"
                             }

            # =============================
            # 🔴 EXTRACT QUOTE
            # =============================
            quote = quote_raw.get("Global Quote", {})

            if not quote or "05. price" not in quote:
                print(f"[Retry {attempt+1}] Invalid quote")
                time.sleep(1)
                continue

            # =============================
            # =============================
            daily = fetch_daily(symbol)

            metrics = compute_metrics(daily) if daily else {
                "trend": "unknown",
                "momentum": "unknown",
                "volatility": "unknown"
            }

            # =============================
            # ✅ SUCCESS
            # =============================
            return {
                "price": float(quote["05. price"]),
                "change": float(quote["09. change"]),
                "percent_change": float(
                    quote["10. change percent"].replace("%", "")
                ),
                "volume": int(quote["06. volume"]),

                "trend": metrics["trend"],
                "momentum": metrics["momentum"],
                "volatility": metrics["volatility"],

                "source": "alpha_vantage",
                "confidence": "high"
            }

        except Exception as e:
            print(f"[Retry {attempt+1}] Error:", e)
            time.sleep(1)

    # =============================
    # ❌ FINAL FAILURE
    # =============================
    return {
        "error": "unavailable",
        "symbol": symbol,
        "confidence": "low"
    }