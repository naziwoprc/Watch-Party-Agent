from langgraph.graph import StateGraph, START, END
from plan import ResearchState, plan_node
from search import search_node
from write import write_node, check_citations, judge_spoilers


def judge_node(state: ResearchState) -> dict:
    return {"spoiler_check": judge_spoilers(state["report"])}


builder = StateGraph(ResearchState)
builder.add_node("plan", plan_node)
builder.add_node("search", search_node)
builder.add_node("write", write_node)
builder.add_node("judge", judge_node)

builder.add_edge(START, "plan")
builder.add_edge("plan", "search")
builder.add_edge("search", "write")
builder.add_edge("write", "judge")
builder.add_edge("judge", END)

graph = builder.compile()

if __name__ == "__main__":
    result = graph.invoke({"question": "Frieren: Beyond Journey's End"})
print(result["report"])
used, invented = check_citations(result["report"], result["sources"])
print("\nInvented citations:", sorted(invented) or "none")
print("Spoiler check:", result["spoiler_check"])
