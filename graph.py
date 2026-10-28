from langgraph.graph import StateGraph, START, END
from plan import ResearchState, plan_node
from search import search_node
from write import write_node, check_citations, judge_spoilers


def judge_node(state: ResearchState) -> dict:
    return {"spoiler_check": judge_spoilers(state["report"])}


MAX_WRITES = 3


def route_after_judge(state: ResearchState) -> str:
    verdict = state["spoiler_check"].strip().upper()
    if verdict.startswith("NONE"):
        return "finish"
    if state.get("revisions", 0) >= MAX_WRITES:
        print("Giving up after", MAX_WRITES, "drafts. Spoilers may remain.")
        return "finish"
    return "revise"


builder = StateGraph(ResearchState)

builder.add_node("plan", plan_node)
builder.add_node("search", search_node)
builder.add_node("write", write_node)
builder.add_node("judge", judge_node)

builder.add_edge(START, "plan")
builder.add_edge("plan", "search")
builder.add_edge("search", "write")
builder.add_edge("write", "judge")

builder.add_conditional_edges(
    "judge",
    route_after_judge,
    {
        "revise": "write",
        "finish": END,
    },
)

graph = builder.compile()


if __name__ == "__main__":
    result = None
    for state in graph.stream(
        {"question": "Frieren: Beyond Journey's End"}, stream_mode="values"
    ):
        print(
            "revisions so far:",
            state.get("revisions", 0),
            "| has report:",
            "report" in state,
        )
        result = state

    print(result["report"])
    print("Spoiler check:", result["spoiler_check"])
