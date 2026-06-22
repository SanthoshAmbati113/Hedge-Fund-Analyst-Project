from agents.market_intelligence import market_intelligence_agent

def run():
    state = {
        "stock_symbol": "AAPL"
    }

    result = market_intelligence_agent(state)

    print("\n=== MARKET AGENT TEST ===")
    print(result)

if __name__ == "__main__":
    run()