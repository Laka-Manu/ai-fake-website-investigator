import os
import ssl
import socket
import whois
import base64
from datetime import datetime
try:
    from langchain_groq import ChatGroq
except Exception:  # pragma: no cover
    ChatGroq = None

from langchain_openai import ChatOpenAI
from schemas import NetworkReport, VisionReport, FinalDecision

# Helper Utility Tools to Fetch Real Data 

def get_live_network_data(url: str) -> dict:
    """Fetch real WHOIS and SSL certificate details for a target URL."""
    # Clean domain from URL
    domain = url.replace("https://", "").replace("http://", "").split("/")[0].split(":")[0]
    
    data = {
        "domain": domain,
        "registrar": "Unknown",
        "creation_date": "Unknown",
        "domain_age_days": -1,
        "ssl_issuer": "None",
        "ssl_valid": False,
        "has_ssl": False
    }
    
    # 1. Fetch WHOIS Data
    try:
        w = whois.whois(domain)
        if w.creation_date:
            creation = w.creation_date[0] if isinstance(w.creation_date, list) else w.creation_date
            if isinstance(creation, datetime):
                data["creation_date"] = creation.strftime("%Y-%m-%d")
                data["domain_age_days"] = (datetime.now() - creation).days
        if w.registrar:
            data["registrar"] = w.registrar[0] if isinstance(w.registrar, list) else str(w.registrar)
    except Exception as e:
        data["whois_error"] = str(e)

    # 2. Fetch Live SSL Certificate Data
    try:
        context = ssl.create_default_context()
        with socket.create_connection((domain, 443), timeout=5) as sock:
            with context.wrap_socket(sock, server_hostname=domain) as ssock:
                cert = ssock.getpeercert()
                issuer = dict(x[0] for x in cert.get('issuer', []))
                data["ssl_issuer"] = issuer.get('organizationName', issuer.get('commonName', 'Unknown'))
                data["ssl_valid"] = True
                data["has_ssl"] = True
    except Exception:
        data["has_ssl"] = False
        data["ssl_valid"] = False

    return data


# Agent Implementations 

# 1. Network & SSL Agent
def network_agent(state):
    if ChatGroq is None:
        raise ImportError("langchain_groq is not installed or could not be imported.")
    
    target_url = state.get("url", "")
    
    # Step A: Fetch actual dynamic network and WHOIS data
    real_data = get_live_network_data(target_url)

    llm = ChatGroq(
        model_name="llama-3.1-8b-instant",
        api_key=os.getenv("GROQ_API_KEY"),
        temperature=0.1
    )
    structured_llm = llm.with_structured_output(NetworkReport)
    
    prompt = f"""
    You are a Cybersecurity Network & Domain Investigator.
    Analyze the following LIVE technical network inspection data for the website '{target_url}':

    - Target Domain: {real_data['domain']}
    - Domain Registrar: {real_data['registrar']}
    - Creation Date: {real_data['creation_date']}
    - Domain Age (Days): {real_data['domain_age_days']}
    - Has SSL Certificate: {real_data['has_ssl']}
    - SSL Issuer Organization: {real_data['ssl_issuer']}
    - SSL Certificate Valid: {real_data['ssl_valid']}

    Evaluate if the domain registration age, SSL configuration, or registrar characteristics indicate a newly created phishing lookalike or suspicious domain.
    """
    
    result = structured_llm.invoke(prompt)
    return {"network_report": result.model_dump()}


# 2. Vision Agent
def vision_agent(state):
    llm = ChatOpenAI(
        model="google/gemini-flash-1.5",
        openai_api_base="https://openrouter.ai/api/v1",
        openai_api_key=os.getenv("OPENROUTER_API_KEY"),
        temperature=0.1
    )
    structured_llm = llm.with_structured_output(VisionReport)
    
    screenshot_path = state.get("screenshot_path")
    target_url = state.get("url", "")
    
    # Check if a screenshot image exists on disk to inspect
    if screenshot_path and os.path.exists(screenshot_path):
        with open(screenshot_path, "rb") as image_file:
            encoded_image = base64.b64encode(image_file.read()).decode("utf-8")
        
        prompt_content = [
            {
                "type": "text",
                "text": f"Analyze this website screenshot for target URL '{target_url}'. Detect cloned brand logos, login prompt overlays, fake browser toolbars, or deceptive layouts."
            },
            {
                "type": "image_url",
                "image_url": {"url": f"data:image/png;base64,{encoded_image}"}
            }
        ]
        result = structured_llm.invoke(prompt_content)
    else:
        # Fallback evaluation if no screenshot is captured
        prompt = f"No image screenshot available for {target_url}. Perform vision risk assessment default evaluation assuming standard website rendering."
        result = structured_llm.invoke(prompt)

    return {"vision_report": result.model_dump()}


# 3. Decision Agent
def decision_agent(state):
    if ChatGroq is None:
        raise ImportError("langchain_groq is not installed or could not be imported.")
        
    llm = ChatGroq(
        model_name="llama-3.3-70b-versatile",
        api_key=os.getenv("GROQ_API_KEY"),
        temperature=0.1
    )
    structured_llm = llm.with_structured_output(FinalDecision)
    
    prompt = f"""
    You are the Lead Cybersecurity Investigator.
    Synthesize the individual agent investigation reports for Target URL: {state.get('url')}

    NETWORK & DOMAIN REPORT:
    {state.get('network_report')}

    VISION & LOGO REPORT:
    {state.get('vision_report')}

    RAG SCAM KNOWLEDGE CONTEXT:
    {state.get('rag_context', 'No specific RAG alerts retrieved.')}

    Cross-check all findings. Calculate a final threat risk score between 0 (Completely Safe) and 100 (Critical Phishing Threat).
    Provide a definitive verdict (SAFE, SUSPICIOUS, or PHISHING) and key bullet points explaining your decision.
    """
    
    result = structured_llm.invoke(prompt)
    return {"final_decision": result.model_dump()}