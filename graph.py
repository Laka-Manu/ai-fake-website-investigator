from langgraph.graph import StateGraph, START, END
from schemas import AgentState
from agents import network_agent, vision_agent, decision_agent

# Initialize graph with state schema
builder = StateGraph(AgentState)

# Add Agent Nodes
builder.add_node("network_agent", network_agent)
builder.add_node("vision_agent", vision_agent)
builder.add_node("decision_agent", decision_agent)

# --- Parallel Fan-Out / Fan-In Workflow ---
# 1. Parallel Fan-Out: Run network and vision agents concurrently from START
builder.add_edge(START, "network_agent")
builder.add_edge(START, "vision_agent")

# 2. Parallel Fan-In: Aggregate outputs from both agents into the decision agent
builder.add_edge("network_agent", "decision_agent")
builder.add_edge("vision_agent", "decision_agent")

# 3. Exit workflow
builder.add_edge("decision_agent", END)

# Compile Graph Workflow
graph = builder.compile()

# Local Execution Test
if __name__ == "__main__":
    initial_input = {
        "url": "https://paypal-secure-login-attempt.com",
        "screenshot_path": "uploads/screenshot.png"
    }

    print(" Orchestration pipeline starting...\n")
    final_output = graph.invoke(initial_input)

    print("--- FINAL DECISION ---")
    decision = final_output.get("final_decision", {})
    print(f"Risk Score : {decision.get('risk_score', 'N/A')}")
    print(f"Verdict    : {decision.get('verdict', 'N/A')}")
    print(f"Reasoning  : {decision.get('reasons', 'N/A')}")