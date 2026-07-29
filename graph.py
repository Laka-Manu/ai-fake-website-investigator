# graph.py
from langgraph.graph import StateGraph, START, END
from schemas import AgentState
from agents import network_agent, vision_agent, decision_agent


builder = StateGraph(AgentState)

builder.add_node("network_agent", network_agent)
builder.add_node("vision_agent", vision_agent)
builder.add_node("decision_agent", decision_agent)


builder.set_entry_point("network_agent")
builder.add_edge("network_agent", "vision_agent")
builder.add_edge("vision_agent", "decision_agent")
builder.add_edge("decision_agent", END)


app = builder.compile()

if __name__ == "__main__":
    initial_input = {
        "url": "https://paypal-secure-login-attempt.com",
        "screenshot_path": "uploads/screenshot.png"
    }

    print("Starting Orchestration pipeline...\n")
    final_output = app.invoke(initial_input)

    print("---  FINAL DECISION ---")
    print(f"Risk Score : {final_output['final_decision']['risk_score']}")
    print(f"Verdict    : {final_output['final_decision']['verdict']}")
    print(f"Reasoning  : {final_output['final_decision']['reasoning']}")