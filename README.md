
# AI Fake Website Investigator (Agentic AI System)

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://ai-fake-website-investigator.streamlit.app)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![LangGraph](https://img.shields.io/badge/Orchestration-LangGraph-orange.svg)](https://github.com/langchain-ai/langgraph)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

> **Horizon Campus — Faculty of Information Technology**  
> **IT41043 — Intelligent Systems (Agentic AI)**  
> **Live Application URL:** [https://ai-fake-website-investigator-furhafrcedzo4kpy4khpvw.streamlit.app/](https://ai-fake-website-investigator.streamlit.app)  
> **GitHub Repository:** [https://github.com/Laka-Manu/ai-fake-website-investigator.git](https://github.com/Laka-Manu/ai-fake-website-investigator)

---

## 1. Project Overview & Problem Statement

Phishing, credential harvesting, and brand impersonation remain major digital security threats, particularly in emerging markets like Sri Lanka. Bad actors frequently register lookalike domains targeting Sri Lankan commercial banks (e.g., Commercial Bank, HNB, Sampath Bank), government utility portals, and payment gateways (LankaPay, eZ Cash).

The **AI Fake Website Investigator** is an autonomous, multi-agent cybersecurity inspection application. Given a target URL, the system fans out to four specialized diagnostic agents (HTML, SSL, WHOIS Domain Reputation, and Screenshot Vision) that perform deep heuristic and visual checks. Their structured outputs are synthesized alongside a domain-specific **Phishing Knowledge Base (RAG)** by a high-reasoning decision agent to produce a final threat score and risk verdict.

---

## 2. System Architecture

The application uses **LangGraph** to implement a parallel fan-out / fan-in orchestrator pattern.

```mermaid
graph TD
    A[User Input: Target URL] --> B[Streamlit UI Engine]
    B --> C[LangGraph State Orchestrator]
    
    subgraph Parallel Diagnostic Agents
        C -->|Raw HTML| D[Agent 1: HTML Auditor<br/>Groq - Llama 3.1 8B]
        C -->|SSL Handshake| E[Agent 2: SSL Cert Auditor<br/>Groq - Llama 3.1 8B]
        C -->|WHOIS Lookup| F[Agent 3: Domain Reputation<br/>Groq - Llama 3.1 8B]
        C -->|Screenshot Base64| G[Agent 4: Vision Analyst<br/>OpenRouter - Gemini 2.5 Flash]
    end
    
    D -->|JSON Report| H[Agent 5: Lead Security Investigator<br/>Groq - Llama 3.3 70B]
    E -->|JSON Report| H
    F -->|JSON Report| H
    G -->|JSON Report| H
    
    I[(Phishing Knowledge Base<br/>FAISS + MiniLM Embeddings)] -->|Relevant Scam Rules| H
    
    H --> J[Final Verdict: SAFE / SUSPICIOUS / PHISHING]
    J --> K[Streamlit UI Dashboard & PDF Audit]

    ## 4. Agent-to-Agent Communication Protocol

Agents exchange state through a strictly typed `InvestigatorState` schema (`src/state.py`). Each diagnostic agent accepts raw metadata and emits a validated JSON report adhering to a predefined Pydantic interface.

```mermaid
sequenceDiagram
    autonumber
    participant UI as Streamlit App
    participant Graph as LangGraph Orchestrator
    participant Agents as Diagnostic Agents (HTML / SSL / Domain / Vision)
    participant VectorStore as FAISS Phishing RAG
    participant Lead as Final Decision Agent

    UI->>Graph: Invoke graph with URL State
    Graph->>Agents: Fan-out: Execute diagnostic agents in parallel
    Agents-->>Graph: Return structured JSON reports
    Graph->>VectorStore: Query similarity search (e.g., "bank domain spoofing")
    VectorStore-->>Graph: Return top-k relevant knowledge chunks
    Graph->>Lead: Aggregate 4 JSON reports + RAG Context
    Lead-->>UI: Return Final Verdict, Risk Score (0-100), and Reasons

    