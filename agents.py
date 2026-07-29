import os
import requests
import whois
from urllib.parse import urlparse
import streamlit as st
from langchain_openai import ChatOpenAI
from langchain_groq import ChatGroq
from schemas import AgentState

# Load API keys from Streamlit secrets if available
if "GROQ_API_KEY" in st.secrets:
    os.environ["GROQ_API_KEY"] = st.secrets["GROQ_API_KEY"]
if "OPENROUTER_API_KEY" in st.secrets:
    os.environ["OPENROUTER_API_KEY"] = st.secrets["OPENROUTER_API_KEY"]


# --- 1. NETWORK AGENT ---
def network_agent(state: AgentState) -> dict:
    url = state["url"]
    domain = urlparse(url).netloc or url
    
    network_info = {
        "domain": domain,
        "creation_date": "Unknown",
        "registrar": "Unknown",
        "ip_address": "Unknown"
    }

    try:
        w = whois.whois(domain)
        creation_date = w.creation_date
        if isinstance(creation_date, list):
            creation_date = creation_date[0]
        network_info["creation_date"] = str(creation_date) if creation_date else "Unknown"
        network_info["registrar"] = str(w.registrar) if w.registrar else "Unknown"
    except Exception as e:
        network_info["whois_error"] = str(e)

    return {"network_data": network_info}


# --- 2. VISION AGENT ---
def vision_agent(state: AgentState) -> dict:
    screenshot_path = state.get("screenshot_path", "")
    
    # Check if we have OpenRouter or Groq configured
    openrouter_key = os.getenv("OPENROUTER_API_KEY")
    groq_key = os.getenv("GROQ_API_KEY")

    if openrouter_key:
        # OpenRouter Fix: max_tokens=1000 prevents 402 Insufficient Credit errors
        llm = ChatOpenAI(
            model="google/gemini-2.0-flash-001",
            openai_api_key=openrouter_key,
            openai_api_base="https://openrouter.ai/api/v1",
            max_tokens=1000
        )
    elif groq_key:
        # Fallback to Groq if OpenRouter is not set
        llm = ChatGroq(
            model="llama-3.1-8b-instant",
            groq_api_key=groq_key,
            max_tokens=1000
        )
    else:
        return {"vision_data": {"visual_risk": "Low", "notes": "No API key provided for Vision analysis."}}

    prompt = f"Analyze website features for potential phishing indicators. Target URL: {state.get('url')}"
    
    try:
        response = llm.invoke(prompt)
        return {"vision_data": {"analysis": response.content}}
    except Exception as e:
        return {"vision_data": {"error": str(e)}}

# --- 3. DECISION AGENT (Updated Parser) ---
def decision_agent(state: AgentState) -> dict:
    network = state.get("network_data", {})
    vision = state.get("vision_data", {})

    groq_key = os.getenv("GROQ_API_KEY")
    openrouter_key = os.getenv("OPENROUTER_API_KEY")

    if groq_key:
        llm = ChatGroq(model="llama-3.1-8b-instant", groq_api_key=groq_key, max_tokens=1000)
    elif openrouter_key:
        llm = ChatOpenAI(
            model="google/gemini-2.0-flash-001",
            openai_api_key=openrouter_key,
            openai_api_base="https://openrouter.ai/api/v1",
            max_tokens=1000
        )
    else:
        return {
            "final_decision": {
                "risk_score": 50,
                "verdict": "SUSPICIOUS",
                "reasoning": "Completed network analysis. Enable LLM secrets for full AI reasoning."
            }
        }

    prompt = f"""
    Evaluate website legitimacy based on this collected data:
    - URL: {state.get('url')}
    - Network Data: {network}
    - Vision Data: {vision}

    Respond strictly in this format:
    Risk Score: <0-100>
    Verdict: <SAFE / SUSPICIOUS / MALICIOUS>
    Reasoning: <short summary>
    """

    try:
        response_text = llm.invoke(prompt).content
        
        # Default values
        verdict = "SUSPICIOUS"
        risk_score = 50

        # Dynamically determine verdict from response
        if "MALICIOUS" in response_text.upper():
            verdict = "MALICIOUS"
            risk_score = 85
        elif "SUSPICIOUS" in response_text.upper():
            verdict = "SUSPICIOUS"
            risk_score = 65
        elif "SAFE" in response_text.upper():
            verdict = "SAFE"
            risk_score = 10

        return {
            "final_decision": {
                "risk_score": risk_score,
                "verdict": verdict,
                "reasoning": response_text
            }
        }
    except Exception as e:
        return {
            "final_decision": {
                "risk_score": 50,
                "verdict": "UNKNOWN",
                "reasoning": f"Decision agent error: {str(e)}"
            }
        }