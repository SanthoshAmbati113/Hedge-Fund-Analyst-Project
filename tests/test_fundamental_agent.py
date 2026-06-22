from agents.fundamental_analysis import fundamentals_agent

def run():
    state = {
        "stock_symbol": "GOOGL"
    }

    result = fundamentals_agent(state)

    print("\n=== FUNDAMENTALS AGENT TEST ===")
    print("--------------------------------")

    fa = result["fundamental_analysis"]

    print("\n--- SIGNALS ---")
    for k, v in fa["signals"].items():
        print(f"{k}: {v}")

    print("\n--- SUMMARY ---")
    print(fa["summary"])

    print("\n--- RAW DATA KEYS ---")
    print(list(fa["raw_data"].keys()))

if __name__ == "__main__":
    run()