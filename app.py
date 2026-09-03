import streamlit as st
import requests


# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="Hedge Fund AI Analyst",
    page_icon="📈",
    layout="wide"
)


# ============================================================
# TITLE
# ============================================================

st.title("📊 Hedge Fund AI Analyst")

st.markdown(
    """
    **Multi-Agent Financial Intelligence System**

    Analyze a company using:
    **Market Intelligence → Fundamentals → News → Risk → Final Thesis**
    """
)


# ============================================================
# INPUT INFORMATION
# ============================================================

st.info(
    "Enter a stock symbol such as AAPL, TSLA, NVDA, "
    "or a company name such as Apple or Tesla."
)


# ============================================================
# INPUT
# ============================================================

stock = st.text_input(
    "Enter Stock Symbol or Company Name",
    placeholder="e.g. AAPL or Tesla"
)


run_button = st.button(
    "🚀 Run Full Analysis",
    use_container_width=True
)


# ============================================================
# RUN ANALYSIS
# ============================================================

if run_button:

    if not stock.strip():

        st.warning(
            "Please enter a stock symbol or company name."
        )

        st.stop()


    try:

        with st.spinner(
            "Running market, fundamental, news, risk and thesis agents..."
        ):

            response = requests.post(

                "http://localhost:8000/analyze",

                json={
                    "stock_name": stock
                },

                timeout=300
            )


        # ----------------------------------------------------
        # API ERROR
        # ----------------------------------------------------

        if response.status_code != 200:

            try:
                error_data = response.json()

                st.error(
                    f"❌ API Error: "
                    f"{error_data.get('detail', error_data)}"
                )

            except Exception:

                st.error(
                    f"❌ API Error: {response.text}"
                )

            st.stop()


        data = response.json()


    # --------------------------------------------------------
    # CONNECTION ERROR
    # --------------------------------------------------------

    except requests.exceptions.ConnectionError:

        st.error(
            "❌ Could not connect to FastAPI backend."
        )

        st.info(
            "Make sure FastAPI is running on "
            "http://localhost:8000"
        )

        st.stop()


    # --------------------------------------------------------
    # TIMEOUT
    # --------------------------------------------------------

    except requests.exceptions.Timeout:

        st.error(
            "⏳ Analysis timed out. "
            "The multi-agent workflow took too long."
        )

        st.stop()


    # --------------------------------------------------------
    # GENERAL ERROR
    # --------------------------------------------------------

    except Exception as e:

        st.error(
            f"❌ {str(e)}"
        )

        st.stop()


    # ========================================================
    # EXTRACT RESULTS
    # ========================================================

    thesis = data.get(
        "final_thesis",
        {}
    )

    market = data.get(
        "market_intelligence",
        {}
    )

    fundamentals = data.get(
        "fundamental_analysis",
        {}
    )

    news = data.get(
        "news_narrative",
        {}
    )

    risk = data.get(
        "risk_scenario",
        {}
    )


    # ========================================================
    # ANALYSIS COMPLETE
    # ========================================================

    st.success(
        f"Analysis Complete — "
        f"{data.get('stock_symbol', stock).upper()}"
    )


    # ========================================================
    # FINAL INVESTMENT VIEW
    # ========================================================

    st.header("🎯 Final Investment View")


    recommendation = thesis.get(
        "recommendation",
        "N/A"
    ).upper()

    conviction = thesis.get(
        "conviction",
        "N/A"
    ).upper()

    risk_level = thesis.get(
        "risk_level",
        risk.get("risk_level", "N/A")
    ).upper()

    risk_score = thesis.get(
        "risk_score",
        risk.get("overall_risk_score", None)
    )


    col1, col2, col3, col4 = st.columns(4)


    col1.metric(
        "Recommendation",
        recommendation
    )


    col2.metric(
        "Conviction",
        conviction
    )


    col3.metric(
        "Risk Level",
        risk_level
    )


    if risk_score is not None:

        col4.metric(
            "Risk Score",
            f"{risk_score}/100"
        )

    else:

        col4.metric(
            "Risk Score",
            "N/A"
        )


    # ========================================================
    # FINAL SUMMARY
    # ========================================================

    st.subheader("🧠 Investment Thesis")

    st.write(
        thesis.get(
            "final_summary",
            "No final summary available."
        )
    )


    # ========================================================
    # BULL / BEAR CASE
    # ========================================================

    st.divider()

    col1, col2 = st.columns(2)


    # --------------------------------------------------------
    # BULL CASE
    # --------------------------------------------------------

    with col1:

        st.subheader("🟢 Bull Case")

        bull_case = thesis.get(
            "bull_case",
            []
        )

        if bull_case:

            for point in bull_case:

                with st.expander(
                    point.get(
                        "title",
                        "Bull Case"
                    )
                ):

                    st.write(
                        point.get(
                            "explanation",
                            ""
                        )
                    )

                    evidence = point.get(
                        "evidence",
                        []
                    )

                    if evidence:

                        st.markdown(
                            "**Evidence**"
                        )

                        for item in evidence:

                            st.write(
                                f"• {item}"
                            )

        else:

            st.write(
                "No bull case available."
            )


    # --------------------------------------------------------
    # BEAR CASE
    # --------------------------------------------------------

    with col2:

        st.subheader("🔴 Bear Case")

        bear_case = thesis.get(
            "bear_case",
            []
        )

        if bear_case:

            for point in bear_case:

                with st.expander(
                    point.get(
                        "title",
                        "Bear Case"
                    )
                ):

                    st.write(
                        point.get(
                            "explanation",
                            ""
                        )
                    )

                    evidence = point.get(
                        "evidence",
                        []
                    )

                    if evidence:

                        st.markdown(
                            "**Evidence**"
                        )

                        for item in evidence:

                            st.write(
                                f"• {item}"
                            )

        else:

            st.write(
                "No bear case available."
            )


    # ========================================================
    # CATALYSTS & RISKS
    # ========================================================

    st.divider()

    col1, col2 = st.columns(2)


    # --------------------------------------------------------
    # CATALYSTS
    # --------------------------------------------------------

    with col1:

        st.subheader("⚡ Key Catalysts")

        catalysts = thesis.get(
            "key_catalysts",
            []
        )

        if catalysts:

            for catalyst in catalysts:

                st.write(
                    f"• {catalyst}"
                )

        else:

            st.write(
                "No major catalysts identified."
            )


    # --------------------------------------------------------
    # RISKS
    # --------------------------------------------------------

    with col2:

        st.subheader("⚠️ Key Risks")

        risks = thesis.get(
            "key_risks",
            []
        )

        if risks:

            for item in risks:

                st.write(
                    f"• {item}"
                )

        else:

            st.write(
                "No major risks identified."
            )


    # ========================================================
    # VALUATION
    # ========================================================

    st.divider()

    st.subheader("💰 Valuation View")

    st.write(
        thesis.get(
            "valuation_view",
            "No valuation assessment available."
        )
    )


    # ========================================================
    # RISK / REWARD
    # ========================================================

    st.subheader("⚖️ Risk–Reward Assessment")

    st.write(
        thesis.get(
            "risk_reward_summary",
            "No risk-reward assessment available."
        )
    )


    # ========================================================
    # UPSTREAM ANALYSIS
    # ========================================================

    st.divider()

    st.header("🔍 Detailed Agent Analysis")


    # --------------------------------------------------------
    # MARKET INTELLIGENCE
    # --------------------------------------------------------

    with st.expander(
        "📈 Market Intelligence",
        expanded=False
    ):

        st.json(market)


    # --------------------------------------------------------
    # FUNDAMENTAL ANALYSIS
    # --------------------------------------------------------

    with st.expander(
        "📊 Fundamental Analysis",
        expanded=False
    ):

        st.json(fundamentals)


    # --------------------------------------------------------
    # NEWS NARRATIVE
    # --------------------------------------------------------

    with st.expander(
        "📰 News Narrative",
        expanded=False
    ):

        st.json(news)


    # --------------------------------------------------------
    # RISK ASSESSMENT
    # --------------------------------------------------------

    with st.expander(
        "⚠️ Risk Assessment",
        expanded=False
    ):

        st.json(risk)


    # ========================================================
    # RAW FINAL THESIS
    # ========================================================

    with st.expander(
        "🧾 Raw Final Thesis JSON",
        expanded=False
    ):

        st.json(thesis)