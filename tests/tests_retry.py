from tools.market_data_tools import get_market_data
import time

def run():
    for i in range(3):
        print(f"\nRun {i+1}")
        data = get_market_data("AAPL")
        print(data)
        time.sleep(5)

if __name__ == "__main__":
    run()