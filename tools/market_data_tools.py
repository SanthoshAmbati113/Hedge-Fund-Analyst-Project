import requests
import os
import time
import numpy as np
from dotenv import load_dotenv

import logfire

load_dotenv()

API_KEY =os.getenv('ALPHA_VANTAGE_API_KEY2')
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
        time.sleep(12 - (now - LAST_CALL))

    LAST_CALL = time.time()


# ============================================================
# GENERIC API REQUEST
# ============================================================

def api_request(params):

    throttle()

    response = requests.get(
        BASE_URL,
        params=params,
        timeout=10
    )

    response.raise_for_status()

    return response.json()


# ============================================================
# 1. GLOBAL QUOTE
# ============================================================

def fetch_quote(symbol):

    params = {
        "function": "GLOBAL_QUOTE",
        "symbol": symbol,
        "apikey": API_KEY
    }

    return api_request(params)


# ============================================================
# 2. WEEKLY TIME SERIES
# ============================================================

def fetch_weekly(symbol):

    params = {
        "function": "TIME_SERIES_WEEKLY",
        "symbol": symbol,
        "apikey": API_KEY
    }

    data = api_request(params)

    return data.get("Weekly Time Series", {})


# ============================================================
# API RESPONSE VALIDATION
# ============================================================

def valid_response(data):

    if not data or not isinstance(data, dict):
        return False

    if "Information" in data:
        return False

    if "Note" in data:
        return False

    return True


# ============================================================
# EXTRACT CURRENT QUOTE
# ============================================================

def extract_quote(data):

    quote = data.get("Global Quote", {})

    if not quote or "05. price" not in quote:
        return None

    return {
        "price": float(quote["05. price"]),
        "change": float(quote["09. change"]),
        "percent_change": float(
            quote["10. change percent"].replace("%", "")
        ),
        "volume": int(quote["06. volume"])
    }


# ============================================================
# COMPUTE WEEKLY METRICS
# ============================================================

def compute_weekly_metrics(weekly_data):

    if not weekly_data:

        return {
            "return_3m": None,
            "return_6m": None,
            "return_1y": None,
            "volatility": None,
            "ma_4": None,
            "ma_12": None,
            "ma_26": None,
            "trend": "unknown",
            "momentum": "unknown"
        }

    try:

        # ----------------------------------------------------
        # Alpha Vantage returns newest → oldest
        # ----------------------------------------------------

        dates = list(weekly_data.keys())

        # We only need the most recent 52 weeks
        dates = dates[:52]

        closes = [
            float(weekly_data[d]["4. close"])
            for d in dates
        ]

        if len(closes) < 4:
            raise ValueError("Not enough weekly data")

        latest = closes[0]

        # ====================================================
        # RETURNS
        # ====================================================

        # Approximately 3 months
        price_3m = closes[
            min(12, len(closes) - 1)
        ]

        # Approximately 6 months
        price_6m = closes[
            min(25, len(closes) - 1)
        ]

        # Approximately 1 year
        price_1y = closes[-1]

        return_3m = (
            (latest - price_3m)
            / price_3m
        ) * 100

        return_6m = (
            (latest - price_6m)
            / price_6m
        ) * 100

        return_1y = (
            (latest - price_1y)
            / price_1y
        ) * 100

        # ====================================================
        # WEEKLY VOLATILITY
        # ====================================================

        weekly_returns = []

        for i in range(len(closes) - 1):

            r = (
                (closes[i] - closes[i + 1])
                / closes[i + 1]
            )

            weekly_returns.append(r)

        # Annualized volatility
        volatility = (
            np.std(weekly_returns)
            * np.sqrt(52)
            * 100
        )

        # ====================================================
        # MOVING AVERAGES
        # ====================================================

        ma_4 = np.mean(closes[:4])

        ma_12 = (
            np.mean(closes[:12])
            if len(closes) >= 12
            else None
        )

        ma_26 = (
            np.mean(closes[:26])
            if len(closes) >= 26
            else None
        )

        # ====================================================
        # TREND
        # ====================================================

        if ma_26 is None:

            trend = "unknown"

        elif latest > ma_12 > ma_26:

            trend = "strong_uptrend"

        elif latest < ma_12 < ma_26:

            trend = "strong_downtrend"

        elif latest > ma_26:

            trend = "uptrend"

        elif latest < ma_26:

            trend = "downtrend"

        else:

            trend = "sideways"

        # ====================================================
        # MOMENTUM
        # ====================================================

        if ma_4 > ma_12:

            momentum = "positive"

        elif ma_4 < ma_12:

            momentum = "negative"

        else:

            momentum = "neutral"

        return {

            "return_3m": round(return_3m, 2),
            "return_6m": round(return_6m, 2),
            "return_1y": round(return_1y, 2),

            "volatility": round(
                volatility,
                2
            ),

            "ma_4": round(ma_4, 2),

            "ma_12": (
                round(ma_12, 2)
                if ma_12 is not None
                else None
            ),

            "ma_26": (
                round(ma_26, 2)
                if ma_26 is not None
                else None
            ),

            "trend": trend,
            "momentum": momentum
        }

    except Exception as e:

        print("Weekly metric error:", e)

        return {
            "return_3m": None,
            "return_6m": None,
            "return_1y": None,
            "volatility": None,
            "ma_4": None,
            "ma_12": None,
            "ma_26": None,
            "trend": "unknown",
            "momentum": "unknown"
        }


# ============================================================
# MAIN FUNCTION
# ============================================================

@logfire.instrument("tool:get_market_data", extract_args=False, record_return=False)
def get_market_data(symbol, retries=2):

    """
    Two API calls only:

        1. GLOBAL_QUOTE
        2. TIME_SERIES_WEEKLY

    GLOBAL_QUOTE:
        - Current price
        - Current change
        - Current percentage change
        - Volume

    WEEKLY:
        - 3-month return
        - 6-month return
        - 1-year return
        - Volatility
        - Moving averages
        - Trend
        - Momentum
    """

    logfire.info(
        "market data fetch started",
        tool="get_market_data",
        symbol=symbol,
        retries=retries,
    )

    for attempt in range(retries):

        try:

            # =================================================
            # API CALL 1
            # =================================================

            with logfire.span(
                "external_api:alpha_vantage_global_quote",
                provider="alpha_vantage",
                symbol=symbol,
                attempt=attempt + 1,
            ):
                quote_raw = fetch_quote(symbol)

            if not valid_response(quote_raw):

                return {
                    "error": "invalid_quote_response",
                    "symbol": symbol,
                    "confidence": "low"
                }

            quote = extract_quote(quote_raw)

            if quote is None:

                print(
                    f"[Retry {attempt + 1}] "
                    "Invalid quote"
                )

                time.sleep(1)
                continue

            # =================================================
            # API CALL 2
            # =================================================

            with logfire.span(
                "external_api:alpha_vantage_weekly_series",
                provider="alpha_vantage",
                symbol=symbol,
                attempt=attempt + 1,
            ):
                weekly_raw = fetch_weekly(symbol)

            if not valid_response(weekly_raw):

                return {
                    "error": "invalid_weekly_response",
                    "symbol": symbol,
                    "confidence": "low"
                }

            # =================================================
            # CALCULATE METRICS
            # =================================================

            weekly_metrics = compute_weekly_metrics(
                weekly_raw
            )

            # =================================================
            # FINAL RESULT
            # =================================================

            return {

                "symbol": symbol,

                # ---------------------------------------------
                # CURRENT MARKET STATE
                # ---------------------------------------------

                "price": quote["price"],
                "change": quote["change"],
                "percent_change": quote["percent_change"],
                "volume": quote["volume"],

                # ---------------------------------------------
                # HISTORICAL RETURNS
                # ---------------------------------------------

                "return_3m": weekly_metrics["return_3m"],
                "return_6m": weekly_metrics["return_6m"],
                "return_1y": weekly_metrics["return_1y"],

                # ---------------------------------------------
                # RISK / VOLATILITY
                # ---------------------------------------------

                "volatility": weekly_metrics["volatility"],

                # ---------------------------------------------
                # TREND / MOMENTUM
                # ---------------------------------------------

                "ma_4": weekly_metrics["ma_4"],
                "ma_12": weekly_metrics["ma_12"],
                "ma_26": weekly_metrics["ma_26"],

                "trend": weekly_metrics["trend"],
                "momentum": weekly_metrics["momentum"],

                # ---------------------------------------------
                # METADATA
                # ---------------------------------------------

                "source": "alpha_vantage",
                "confidence": "high"
            }

        except Exception as e:

            print(
                f"[Retry {attempt + 1}] Error:",
                e
            )

            time.sleep(1)

    # =========================================================
    # FINAL FAILURE
    # =========================================================

    return {
        "error": "unavailable",
        "symbol": symbol,
        "confidence": "low"
    }