import streamlit as st
import requests

# ----------------------------------------
# Page Config
# ----------------------------------------
st.set_page_config(
    page_title="Hedge Fund AI",
    page_icon="📈",
    layout="wide"
)

# ----------------------------------------
# Title
# ----------------------------------------
st.title("📊 Hedge Fund AI Analyst")
st.markdown("Analyze stocks using multi-agent AI system")

# ----------------------------------------
# Input Note
# ----------------------------------------
st.info(
    "Use stock symbols like AAPL or TSLA for best results. "
    "You can also enter company names like Tesla or Apple."
)

# ----------------------------------------
# Input
# ----------------------------------------
stock = st.text_input(
    "Enter Stock Symbol or Company Name",
    placeholder="e.g., AAPL or Tesla"
)

run_button = st.button("Run Analysis")

# ----------------------------------------
# Run Analysis
# ----------------------------------------
if run_button and stock:

    try:
        with st.spinner("Running AI analysis..."):

            # 🔥 FastAPI request
            response = requests.post(
                "http://localhost:8000/analyze",
                json={"stock_name": stock},
                timeout=300
            )

            # 🔴 API failure
            if response.status_code != 200:
                st.error(f"❌ API Error: {response.text}")
                st.stop()

            data = response.json()

    except requests.exceptions.ConnectionError:
        st.error("❌ Could not connect to FastAPI backend.")
        st.info("Make sure FastAPI server is running on port 8000.")
        st.stop()

    except Exception as e:
        st.error(f"❌ {str(e)}")
        st.stop()

    # ----------------------------------------
    # Extract thesis
    # ----------------------------------------
    thesis = data["final_thesis"]

    # ----------------------------------------
    # HEADER
    # ----------------------------------------
    st.success("Analysis Complete")

    col1, col2, col3 = st.columns(3)

    col1.metric("Recommendation", thesis["recommendation"].upper())
    col2.metric("Conviction", thesis["conviction"].upper())
    col3.metric("Risk Level", thesis.get("risk_level", "N/A"))

    # ----------------------------------------
    # BULL CASE
    # ----------------------------------------
    st.subheader("🟢 Bull Case")

    for point in thesis["bull_case"]:
        with st.expander(point["title"]):
            st.write(point["explanation"])

            st.write("**Evidence:**")
            for e in point["evidence"]:
                st.write(f"- {e}")

    # ----------------------------------------
    # BEAR CASE
    # ----------------------------------------
    st.subheader("🔴 Bear Case")

    for point in thesis["bear_case"]:
        with st.expander(point["title"]):
            st.write(point["explanation"])

            st.write("**Evidence:**")
            for e in point["evidence"]:
                st.write(f"- {e}")

    # ----------------------------------------
    # CATALYSTS & RISKS
    # ----------------------------------------
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("⚡ Key Catalysts")

        for c in thesis["key_catalysts"]:
            st.write(f"- {c}")

    with col2:
        st.subheader("⚠️ Key Risks")

        for r in thesis["key_risks"]:
            st.write(f"- {r}")

    # ----------------------------------------
    # VALUATION
    # ----------------------------------------
    st.subheader("💰 Valuation View")
    st.write(thesis["valuation_view"])

    # ----------------------------------------
    # RISK-REWARD
    # ----------------------------------------
    st.subheader("⚖️ Risk–Reward Summary")
    st.write(thesis["risk_reward_summary"])

    # ----------------------------------------
    # FINAL SUMMARY
    # ----------------------------------------
    st.subheader("🧠 Final Summary")
    st.write(thesis["final_summary"])