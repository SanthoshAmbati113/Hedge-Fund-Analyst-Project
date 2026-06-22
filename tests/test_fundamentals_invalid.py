from agents.fundamental_analysis import fundamentals_agent

def run():
    state = {
        "stock_symbol": "INVALID123"
    }

    result = fundamentals_agent(state)

    print("\n=== INVALID STOCK TEST ===")
    print("--------------------------------")

    fa = result["fundamental_analysis"]

    print("\n--- SIGNALS ---")
    for k, v in fa["signals"].items():
        print(f"{k}: {v}")

    print("\n--- SUMMARY ---")
    print(fa["summary"])

if __name__ == "__main__":
    run()