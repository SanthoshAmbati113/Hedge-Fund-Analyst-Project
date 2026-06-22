from tools.fundamental_tools import get_fundamentals

def run():
    symbol = "AAPL"

    data = get_fundamentals(symbol)

    print("\n=== FUNDAMENTAL TOOL TEST ===")
    print("Symbol:", symbol)
    print("----------------------------")

    if "error" in data:
        print("❌ ERROR:", data)
        return

    for k, v in data.items():
        print(f"{k}: {v}")

if __name__ == "__main__":
    run()