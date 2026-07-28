# agents.py
import os
try:
    # preferred import
    from langchain_groq import ChatGroq
except Exception:  # pragma: no cover - fallback for environments without the package
    ChatGroq = None
    # Defer raising an explicit error until runtime when the agent is used.
from langchain_openai import ChatOpenAI
from schemas import NetworkReport, VisionReport, FinalDecision

# 1. Network & SSL Agent
def network_agent(state):
    if ChatGroq is None:
        raise ImportError("langchain_groq is not installed or could not be imported. Install the package and try again.")
    llm = ChatGroq(
        model_name="llama-3.1-8b-instant",
        api_key=os.getenv("GROQ_API_KEY"),
    )
    structured_llm = llm.with_structured_output(NetworkReport)
    
    prompt = f"Analyze network parameters for domain from URL: {state['url']}."
    result = structured_llm.invoke(prompt)
    return {"network_report": result.model_dump()}

# 2. Vision Agent
def vision_agent(state):
    llm = ChatOpenAI(
        model="google/gemini-flash-1.5",
        openai_api_base="https://openrouter.ai/api/v1",
        openai_api_key=os.getenv("OPENROUTER_API_KEY")
    )
    structured_llm = llm.with_structured_output(VisionReport)
    
    prompt = f"Analyze website screenshot at path: {state['screenshot_path']} for spoofed logos."
    result = structured_llm.invoke(prompt)
    return {"vision_report": result.model_dump()}

# 3. Decision Agent
def decision_agent(state):
    if ChatGroq is None:
        raise ImportError("langchain_groq is not installed or could not be imported. Install the package and try again.")
    llm = ChatGroq(
        model_name="llama-3.3-70b-versatile",
        api_key=os.getenv("GROQ_API_KEY"),
    )
    structured_llm = llm.with_structured_output(FinalDecision)
    
    prompt = f"""
    Analyze reports and calculate risk:
    Network Report: {state.get('network_report')}
    Vision Report: {state.get('vision_report')}
    """
    result = structured_llm.invoke(prompt)
    return {"final_decision": result.model_dump()}