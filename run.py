from graph.workflow import build_graph



def render_thesis(thesis: dict):
    print("\nFINAL INVESTMENT THESIS")
    print("=" * 60)

    print(f"\nStock: {thesis['stock_name']}")
    print(f"Recommendation: {thesis['recommendation'].upper()}")
    print(f"Conviction: {thesis['conviction'].upper()}")

    print("\n--- BULL CASE ---")
    for i, point in enumerate(thesis["bull_case"], 1):
        print(f"\n{i}. {point['title']}")
        print(f"   {point['explanation']}")
        print("   Evidence:")
        for e in point["evidence"]:
            print(f"    - {e}")

    print("\n--- BEAR CASE ---")
    for i, point in enumerate(thesis["bear_case"], 1):
        print(f"\n{i}. {point['title']}")
        print(f"   {point['explanation']}")
        print("   Evidence:")
        for e in point["evidence"]:
            print(f"    - {e}")

    print("\n--- KEY CATALYSTS ---")
    for c in thesis["key_catalysts"]:
        print(f" - {c}")

    print("\n--- KEY RISKS ---")
    for r in thesis["key_risks"]:
        print(f" - {r}")

    print("\nValuation View:", thesis["valuation_view"])

    print("\nRisk–Reward Summary:")
    print(thesis["risk_reward_summary"])

    print("\n--- FINAL SUMMARY ---")
    print(thesis["final_summary"])

    print("\n" + "=" * 60)

def run(stock: str):
    app = build_graph()

    initial_state = {
        "stock_name": stock,
        "market_intelligence": {},
        "fundamental_analysis": {},
        "news_narrative": {},
        "risk_scenario": {},
        "final_thesis": {},
        "next_agent": "market_intelligence"
    }

    print(f"\nRunning hedge-fund AI for: {stock}")
    print("=" * 60)
    
    try:
        final_state = app.invoke(initial_state)
    except ValueError as e:
        print("\n❌ ERROR")
        print("=" * 60)
        print(str(e))
        return

    

    render_thesis(final_state["final_thesis"])


if __name__ == "__main__":
    run("FOV")
