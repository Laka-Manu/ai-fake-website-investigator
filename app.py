import sys
import os
import traceback
import streamlit as st
import plotly.graph_objects as go

# 1. Path setup & Graph Import
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from graph import graph
except Exception as e:
    st.error("⚠️ **Error importing `graph.py`**")
    st.code(traceback.format_exc())
    st.stop()


# 2. Page Configuration
st.set_page_config(
    page_title="AI Phishing & Security Investigator",
    page_icon="🛡️",
    layout="wide"
)

st.title("🛡️ Website Phishing & Risk Investigator")
st.write("Enter a website URL below to run multi-agent security checks and view the overall risk score.")


# 3. Helper Function: Gauge Chart Generator
def create_gauge_chart(score):
    try:
        score_val = float(score)
    except (ValueError, TypeError):
        score_val = 0.0

    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=score_val,
        domain={'x': [0, 1], 'y': [0, 1]},
        title={'text': "Overall Risk Score (0-100)"},
        gauge={
            'axis': {'range': [0, 100]},
            'bar': {'color': "darkblue"},
            'steps': [
                {'range': [0, 30], 'color': "#2ecc71"},   # Low Risk (Green)
                {'range': [30, 70], 'color': "#f1c40f"},  # Moderate Risk (Yellow)
                {'range': [70, 100], 'color': "#e74c3c"}  # High Risk (Red)
            ],
            'threshold': {
                'line': {'color': "red", 'width': 4},
                'thickness': 0.75,
                'value': score_val
            }
        }
    ))
    fig.update_layout(height=280, margin=dict(l=20, r=20, t=30, b=20))
    return fig


# 4. Input Section
url_input = st.text_input("Enter Website URL:", placeholder="https://example.com")
investigate_btn = st.button("Investigate Website", type="primary")


# 5. Main Investigation Flow
if investigate_btn:
    if not url_input.strip():
        st.warning("Please enter a valid URL to investigate!")
    else:
        st.divider()
        st.subheader("🕵️ Orchestrating Multi-Agent Pipeline")

        # Initial State passed into LangGraph
        initial_state = {
            "url": url_input.strip(),
            "screenshot_path": "uploads/screenshot.png",
            "network_data": {},
            "vision_data": {},
            "final_decision": {},
            "messages": []
        }

        # Run Graph Execution with real-time UI feedback
        try:
            with st.spinner("🤖 Running LangGraph Agents (Network ➔ Vision ➔ Decision)..."):
                pipeline_result = graph.invoke(initial_state)

            st.success("✅ Multi-Agent Investigation Completed!")
            st.divider()

            # Extract dynamic results from graph
            decision = pipeline_result.get("final_decision", {})
            network_data = pipeline_result.get("network_data", {})
            vision_data = pipeline_result.get("vision_data", {})

            calculated_risk_score = decision.get("risk_score", 0)
            verdict = decision.get("verdict", "UNKNOWN")
            reasoning = decision.get("reasoning", "No detailed reasoning available.")

            # Risk Score Visualization
            col1, col2 = st.columns([1, 2])

            with col1:
                st.plotly_chart(create_gauge_chart(calculated_risk_score), use_container_width=True)

            with col2:
                st.subheader("⚠️ Risk Assessment Summary")
                
                if calculated_risk_score >= 70 or verdict == "MALICIOUS":
                    st.error(f"**HIGH RISK ({verdict}):** This website shows strong indicators of phishing or malicious activity!")
                elif calculated_risk_score >= 30 or verdict == "SUSPICIOUS":
                    st.warning(f"**MODERATE RISK ({verdict}):** Suspicious elements were detected. Proceed with caution.")
                else:
                    st.success(f"**LOW RISK ({verdict}):** The website appears to be safe based on multi-agent scans.")

                st.progress(min(max(calculated_risk_score / 100, 0.0), 1.0))
                st.markdown(f"**AI Reasoning:**\n\n{reasoning}")

            st.divider()

            # Detailed Dynamic Reports in Tabs
            st.subheader("Detailed Investigation Reports")
            tab_network, tab_vision, tab_raw = st.tabs(["🌐 Network & WHOIS Report", "👁️ Vision & Content Report", "📦 Raw Graph State"])

            with tab_network:
                st.markdown("### Network & Domain Intelligence")
                st.json(network_data if network_data else {"status": "No network data collected"})

            with tab_vision:
                st.markdown("### Visual & Content Intelligence")
                st.json(vision_data if vision_data else {"status": "No vision data collected"})

            with tab_raw:
                st.markdown("### Full LangGraph Pipeline Output")
                st.json(pipeline_result)

        except Exception as e:
            st.error(f"❌ Error during multi-agent graph execution: {e}")
            st.code(traceback.format_exc())