import re
from typing import TypedDict
from dotenv import load_dotenv
from langchain_groq import ChatGroq

load_dotenv()


class ResearchState(TypedDict):
    question: str
    queries: list[str]
    sources: list[dict]
    report: str
    spoiler_check: str
    revisions: int


llm = ChatGroq(
    model="openai/gpt-oss-20b",
    temperature=0,
    max_tokens=4096,
)

PLAN_PROMPT = """You are researching a title for a group of friends
deciding what to watch or listen to next.

Title: {question}

Write exactly 5 web search queries, one per line, in this order:
1. audience reviews and critical reception
2. what fans love most
3. common criticisms or divisive points
4. behind-the-scenes trivia and hidden details
5. similar titles fans recommend afterwards

Rules:
- Keep each query under 12 words., like a person typing into Google.
- Include the title in every query.
- Do not include years or dates.
- Do not search for plot summaries or release dates.
- Output only the 5 queries, one per line, no numbering and no extra text."""


def parse_lines(text: str) -> list[str]:
    cleaned = []
    for line in text.splitlines():
        line = re.sub(r"^\s*(?:[-*•]|\d+[.)])\s*", "", line).strip()
        if line:
            cleaned.append(line)
    return cleaned[:5]


def plan_node(state: ResearchState) -> dict:
    reply = llm.invoke(PLAN_PROMPT.format(question=state["question"]))
    queries = parse_lines(reply.content)
    if not queries:
        raise ValueError(f"Planner returned no queries. Raw reply: {reply.content!r}")
    return {"queries": queries}


if __name__ == "__main__":
    reply = llm.invoke(PLAN_PROMPT.format(question="Frieren: Beyond Journey's End"))
    print("CONTENT:", repr(reply.content))
    print("EXTRA:", reply.additional_kwargs)
    print("PARSED:", parse_lines(reply.content))
