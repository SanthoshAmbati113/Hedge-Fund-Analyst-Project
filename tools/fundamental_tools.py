import requests
import os
import time
from dotenv import load_dotenv
from pathlib import Path

import logfire

load_dotenv(Path(__file__).resolve().parents[1] / ".env")

API_KEY = os.getenv("ALPHA_VANTAGE_API_KEY")
BASE_URL = "https://www.alphavantage.co/query"

# -----------------------------
# Throttle
# -----------------------------
LAST_CALL = 0

def throttle():
    global LAST_CALL
    now = time.time()

    if now - LAST_CALL < 12:
        time.sleep(12 - (now - LAST_CALL))

    LAST_CALL = time.time()


# -----------------------------
# Fetch OVERVIEW (only)
# -----------------------------
def fetch_overview(symbol):
    throttle()

    params = {
        "function": "OVERVIEW",
        "symbol": symbol,
        "apikey": API_KEY
    }

    res = requests.get(BASE_URL, params=params, timeout=10)
    data = res.json()

    print("RAW OVERVIEW RESPONSE:", data)  # 🔥 ADD THIS

    return data


# -----------------------------
# MAIN FUNCTION
# -----------------------------
@logfire.instrument("tool:get_fundamentals", extract_args=False, record_return=False)
def get_fundamentals(symbol, retries=2):
    """
    Optimized fundamentals:
    - Single API call (OVERVIEW)
    - Retry logic
    - Extract key financial signals
    """

    for attempt in range(retries):
        try:
            with logfire.span(
                "external_api:alpha_vantage_overview",
                provider="alpha_vantage",
                symbol=symbol,
                attempt=attempt + 1,
            ):
                data = fetch_overview(symbol)

            # 🔴 Validate response
            if not data or "Symbol" not in data:
                print(f"[Retry {attempt+1}] Invalid overview data")
                time.sleep(1)
                continue

            # -----------------------------
            # Extract key metrics
            # -----------------------------
            def safe_float(x):
                try:
                    return float(x)
                except:
                    return None

            revenue = safe_float(data.get("RevenueTTM"))
            profit_margin = safe_float(data.get("ProfitMargin"))
            operating_margin = safe_float(data.get("OperatingMarginTTM"))
            roe = safe_float(data.get("ReturnOnEquityTTM"))
            roa = safe_float(data.get("ReturnOnAssetsTTM"))

            pe = safe_float(data.get("PERatio"))
            pb = safe_float(data.get("PriceToBookRatio"))
            peg = safe_float(data.get("PEGRatio"))

            market_cap = safe_float(data.get("MarketCapitalization"))

            revenue_growth = safe_float(data.get("QuarterlyRevenueGrowthYOY"))
            earnings_growth = safe_float(data.get("QuarterlyEarningsGrowthYOY"))

            dividend_yield = safe_float(data.get("DividendYield"))

            # -----------------------------
            # Confidence logic
            # -----------------------------
            # available_fields = [
            #     revenue, profit_margin, roe, pe, pb, revenue_growth
            # ]

            # filled = sum([1 for x in available_fields if x is not None])

            # if filled >= 5:
            #     confidence = "high"
            # elif filled >= 3:
            #     confidence = "medium"
            # else:
            #     confidence = "low"  its done in the agent itself

            # -----------------------------
            # Final structured output
            # -----------------------------
            return {
                "company_name": data.get("Name"),
                "sector": data.get("Sector"),
                "industry": data.get("Industry"),

                "revenue": revenue,
                "profit_margin": profit_margin,
                "operating_margin": operating_margin,
                "roe": roe,
                "roa": roa,

                "pe_ratio": pe,
                "pb_ratio": pb,
                "peg_ratio": peg,

                "market_cap": market_cap,

                "revenue_growth": revenue_growth,
                "earnings_growth": earnings_growth,

                "dividend_yield": dividend_yield,

                # "confidence": confidence,
                "source": "alpha_vantage_overview"
            }

        except Exception as e:
            print(f"[Retry {attempt+1}] Error:", e)
            time.sleep(1)

    # -----------------------------
    # Final fallback
    # -----------------------------
    return {
        "error": "unavailable",
        "symbol": symbol,
        "confidence": "low"
    }