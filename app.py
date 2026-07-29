import sys
import os
import streamlit as st
import plotly.graph_objects as go

# 1. Force Python to look in the current file directory for modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# 2. Robust import with detailed error logging
try:
    from graph import graph
except Exception as e:
    st.error("**Failed to load the graph workflow!**")
    st.error(f"**Exact Error:** `{e}`")
    st.info(" **Troubleshooting Tips:**\n"
            "1. Ensure `graph.py` is in the root directory alongside `app.py`.\n"
            "2. Verify `graph = builder.compile()` is exported in `graph.py`.\n"
            "3. Check that all packages (`python-whois`, `langchain-groq`, etc.) are listed in `requirements.txt`.\n"
            "4. Verify API Keys (`GROQ_API_KEY`, `OPENROUTER_API_KEY`) are configured in Streamlit Secrets.")
    st.stop()


# Page Configuration
st.set_page_config(
    page_title="AI Phishing & Security Investigator",
    page_icon="🛡️",
    layout="wide"
)

st.title("🛡️ Website Phishing & Risk Investigator")
st.write("Enter a website URL below to run multi-agent security checks and view the overall risk score.")


# Input Section
url_input = st.text_input("Enter Website URL:", placeholder="https://example.com")
investigate_btn = st.button("Investigate Website", type="primary")


# Helper Function: Gauge Chart Generator
def create_gauge_chart(score):
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=score,
        domain={'x': [0, 1], 'y': [0, 1]},
        title={'text': "Overall Risk Score (0-100)"},
        gauge={
            'axis': {'range': [0, 100]},
            'bar': {'color': "#1f77b4"},
            'steps': [
                {'range': [0, 30], 'color': "#2ca02c"},
                {'range': [30, 70], 'color': "#ff7f0e"},
                {'range': [70, 100], 'color': "#d62728"}
            ],
            'threshold': {
                'line': {'color': "red", 'width': 4},
                'thickness': 0.75,
                'value': score
            }
        }
    ))
    fig.update_layout(height=280, margin=dict(l=20, r=20, t=50, b=20))
    return fig


# Main Investigation Flow
if investigate_btn:
    if not url_input.strip():
        st.warning("Please enter a valid URL to investigate!")
    else:
        st.divider()
        st.subheader("🕵️ Investigation Progress")

        # Normalize URL input
        target_url = url_input.strip()
        if not target_url.startswith("http://") and not target_url.startswith("https://"):
            target_url = "https://" + target_url

        # Initial Graph State
        initial_state = {
            "url": target_url,
            "screenshot_path": "uploads/screenshot.png"
        }

        # Run the multi-agent graph with a live Streamlit spinner
        with st.spinner(f"Running multi-agent cybersecurity graph for {target_url}..."):
            try:
                final_output = graph.invoke(initial_state)
            except Exception as e:
                st.error(f"Error during investigation graph execution: {e}")
                st.stop()

        st.success("Multi-Agent Investigation Completed Successfully!")
        st.divider()

        # Extract Results from Final State
        net_report = final_output.get("network_report", {})
        vis_report = final_output.get("vision_report", {})
        decision = final_output.get("final_decision", {})

        # Extract Risk Score and Verdict
        calculated_risk_score = decision.get("risk_score", 50)
        verdict = decision.get("verdict", "SUSPICIOUS").upper()

        # Risk Score & Assessment Dashboard
        col1, col2 = st.columns([1, 2])

        with col1:
            st.plotly_chart(create_gauge_chart(calculated_risk_score), use_container_width=True)

        with col2:
            st.subheader("⚠️ Risk Assessment Summary")
            st.markdown(f"**Final Verdict:** `{verdict}`")

            if calculated_risk_score >= 70 or verdict == "PHISHING":
                st.error(f"**HIGH RISK ({calculated_risk_score}/100):** This website shows strong indicators of phishing or malicious activity!")
            elif calculated_risk_score >= 30 or verdict == "SUSPICIOUS":
                st.warning(f"**MODERATE RISK ({calculated_risk_score}/100):** Suspicious elements were detected. Proceed with caution.")
            else:
                st.success(f"**LOW RISK ({calculated_risk_score}/100):** The website appears to be safe based on initial multi-agent checks.")

            st.progress(min(max(calculated_risk_score / 100, 0.0), 1.0))

            st.markdown("### Key Risk Reasons & Analysis:")
            reasons = decision.get("reasons", ["No specific reasons provided by decision agent."])
            if isinstance(reasons, list):
                for r in reasons:
                    st.write(f"• {r}")
            else:
                st.write(reasons)

        st.divider()

        # Detailed Reports in Tabs
        st.subheader("Detailed Multi-Agent Investigation Reports")
        tab_network, tab_vision, tab_decision = st.tabs([" Network & SSL Report", " Vision Report", " Final Decision JSON"])

        with tab_network:
            st.markdown("### Network & Domain Agent Output")
            if net_report:
                st.json(net_report)
            else:
                st.info("No network report data available.")

        with tab_vision:
            st.markdown("### Vision Agent Output")
            if vis_report:
                st.json(vis_report)
            else:
                st.info("No vision report data available.")

        with tab_decision:
            st.markdown("### Final Decision Agent Raw Output")
            if decision:
                st.json(decision)
            else:
                st.info("No decision output available.")