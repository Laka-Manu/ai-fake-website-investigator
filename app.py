import streamlit as st
import time
import plotly.graph_objects as go

# ----------------------------------------------------
# Page Configuration
# ----------------------------------------------------
st.set_page_config(
    page_title="AI Phishing & Security Investigator",
    page_icon="🛡️",
    layout="wide"
)

st.title("🛡️ Website Phishing & Risk Investigator")
st.write("Enter a website URL below to run multi-agent security checks and view the overall risk score.")

# ----------------------------------------------------
# Input Section
# ----------------------------------------------------
url_input = st.text_input("Enter Website URL:", placeholder="https://example.com")
investigate_btn = st.button("Investigate Website", type="primary")

# ----------------------------------------------------
# Helper Function: Gauge Chart Generator
# ----------------------------------------------------
def create_gauge_chart(score):
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=score,
        domain={'x': [0, 1], 'y': [0, 1]},
        title={'text': "Overall Risk Score (0-100)"},
        gauge={
            'axis': {'range': [0, 100]},
            'bar': {'color': "darkblue"},
            'steps': [
                {'range': [0, 30], 'color': "lightgreen"},
                {'range': [30, 70], 'color': "yellow"},
                {'range': [70, 100], 'color': "salmon"}
            ],
            'threshold': {
                'line': {'color': "red", 'width': 4},
                'thickness': 0.75,
                'value': score
            }
        }
    ))
    return fig

# ----------------------------------------------------
# Main Investigation Flow
# ----------------------------------------------------
if investigate_btn:
    if not url_input.strip():
        st.warning("Please enter a valid URL to investigate!")
    else:
        st.divider()
        st.subheader("🕵️ Investigation Progress")

        # 1. Domain Agent Spinner
        with st.spinner("🌐 Domain Analysis Agent running (WHOIS & DNS checks)..."):
            time.sleep(2)  # Replace with actual function: e.g., domain_data = run_domain_agent(url_input)
            st.success("Domain Analysis Completed!")

        # 2. SSL Agent Spinner
        with st.spinner("🔒 SSL/TLS Certificate Agent running..."):
            time.sleep(2)  # Replace with actual function: e.g., ssl_data = run_ssl_agent(url_input)
            st.success("SSL Analysis Completed!")

        # 3. HTML/Content Agent Spinner
        with st.spinner("📄 HTML & Content Analysis Agent running..."):
            time.sleep(2)  # Replace with actual function: e.g., html_data = run_html_agent(url_input)
            st.success("HTML Analysis Completed!")

        st.divider()

        # ----------------------------------------------------
        # Risk Score Visualization
        # ----------------------------------------------------
        # Mock risk score value (Replace with your calculated risk score logic)
        calculated_risk_score = 75 

        col1, col2 = st.columns([1, 2])

        with col1:
            st.plotly_chart(create_gauge_chart(calculated_risk_score), use_container_width=True)

        with col2:
            st.subheader("⚠️ Risk Assessment Summary")
            if calculated_risk_score >= 70:
                st.error("**HIGH RISK:** This website shows strong indicators of phishing or malicious activity!")
            elif calculated_risk_score >= 30:
                st.warning("**MODERATE RISK:** Suspicious elements were detected. Proceed with caution.")
            else:
                st.success("**LOW RISK:** The website appears to be safe based on initial scans.")

            st.progress(calculated_risk_score / 100)

        st.divider()

        # ----------------------------------------------------
        # Detailed Reports in Tabs
        # ----------------------------------------------------
        st.subheader("📊 Detailed Investigation Reports")
        tab_domain, tab_ssl, tab_html = st.tabs(["🌐 Domain Report", "🔒 SSL/TLS Report", "📄 HTML Report"])

        with tab_domain:
            st.markdown("### Domain Details")
            st.json({
                "Domain Name": url_input,
                "Creation Date": "2023-01-15",
                "Registrar": "Example Registrar LLC",
                "Country": "US",
                "Age": "1 Year 5 Months"
            })

        with tab_ssl:
            st.markdown("### SSL Certificate Details")
            st.json({
                "Issuer": "Let's Encrypt",
                "Valid From": "2024-01-01",
                "Valid To": "2024-04-01",
                "Status": "Valid",
                "Key Size": "2048 bits"
            })

        with tab_html:
            st.markdown("### HTML Content Analysis")
            st.json({
                "Form Actions": "Suspicious external endpoint found",
                "External Scripts": 5,
                "Iframe Count": 1,
                "Phishing Keywords Detected": True
            })