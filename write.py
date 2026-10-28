import re
from dotenv import load_dotenv
from langchain_nvidia_ai_endpoints import ChatNVIDIA
from plan import ResearchState, plan_node
from search import search_node

load_dotenv()

WRITER_MODEL = "minimaxai/minimax-m3.1-flash"

writer_llm = ChatNVIDIA(
    model=WRITER_MODEL, temperature=0.3, max_completion_tokens=8192, timeout=600
)


WRITE_PROMPT = """You write short "watch party briefs" for friends deciding what to watch or listen to.

Title: {title}

Below are numbered sources. Use ONLY facts found in these sources.

{sources}

Write the brief in markdown with exactly these sections:
## The pitch
2-3 sentences. Describe tone and themes only.
## Why fans love it
3 bullet points.
## What divides people
2-3 bullet points.
## Trivia
2-3 bullet points.
## If you liked this, try
2-3 titles, but only titles named in the sources.

Rules:
- Every bullet ends with a citation like [S3]. One ID per bracket, e.g. [S1][S4].
- NEVER mention plot events, arcs, episodes, battles, villains, character fates, or twists. Describe themes, tone, visuals, music and audience reaction only.
- Put ratings, rankings and release facts only under Trivia. "Why fans love it" is for what people enjoy, not for statistics.
- If the sources do not support a section, write "Not enough info found." Do not guess.
- Do not cite an ID that is not in the list.
- Copy numbers, ratings and dates exactly as written in the source. Never round or convert them."""

JUDGE_PROMPT = """You are a spoiler checker.

PREMISE = what the official synopsis or first episode establishes. Allowed.
SPOILER = any event, twist, death, reveal or outcome after the premise. Not allowed.

Brief to check:
{report}

List every line that contains a SPOILER, with a one-line reason.
If there are none, reply exactly: NONE"""


def format_sources(sources: list[dict]) -> str:
    return "\n\n".join(
        f"[{s['id']}] {s['title']}\n{s['snippet'][:600]}" for s in sources
    )


def write_node(state: ResearchState) -> dict:
    prompt = WRITE_PROMPT.format(
        title=state["question"], sources=format_sources(state["sources"])
    )
    feedback = state.get("spoiler_check", "")
    if feedback and not feedback.strip().startswith("NONE"):
        prompt += (
            "\n\nYour previous draft was rejected because it contains spoilers:\n"
            f"{feedback}\n\nPrevious draft:\n{state['report']}\n\n"
            "Rewrite the full brief and remove every spoiler listed above."
        )
    reply = writer_llm.invoke(prompt)
    finish = (reply.response_metadata or {}).get("finish_reason")
    if not reply.content or finish == "length":
        raise ValueError(
            f"Writer failed (finish_reason={finish!r}). Raise the token limit or change model."
        )

    return {"report": reply.content, "revisions": state.get("revisions", 0) + 1}


def check_citations(report: str, sources: list[dict]):
    valid = {s["id"] for s in sources}
    used = set(re.findall(r"\[(S\d+)\]", report))
    return used, used - valid


def judge_spoilers(report: str) -> str:
    return writer_llm.invoke(JUDGE_PROMPT.format(report=report)).content


def check_numbers(report: str, sources: list[dict]) -> list[str]:
    seen = " ".join(s["snippet"][:600] for s in sources)
    body = re.sub(r"\[S\d+\]", "", report)
    nums = set(re.findall(r"\d+(?:\.\d+)?", body))
    return sorted(
        n for n in nums if not re.search(rf"(?<![\d.]){re.escape(n)}(?!\d)", seen)
    )


if __name__ == "__main__":
    state = {"question": "Frieren: Beyond Journey's End"}
    state.update(plan_node(state))
    state.update(search_node(state))
    state.update(write_node(state))

    print(state["report"])
    used, invented = check_citations(state["report"], state["sources"])
    print("\nCited:", sorted(used))
    print("Invented citations:", sorted(invented) or "none")
    print("\nSPOILER CHECK:\n", judge_spoilers(state["report"]))
