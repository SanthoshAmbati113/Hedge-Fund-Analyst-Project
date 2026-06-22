from tools.market_data_tools import get_market_data

def run():
    symbol = "AAPL"

    data = get_market_data(symbol)

    print("\n=== MARKET DATA TEST ===")
    print("Symbol:", symbol)
    print("-----------------------")
    
    for k, v in data.items():
        print(f"{k}: {v}")

if __name__ == "__main__":
    run()