import re
from dotenv import load_dotenv

from plan import ResearchState, plan_node
from search import search_node
from langchain_groq import ChatGroq

load_dotenv()

WRITER_MODEL = "openai/gpt-oss-120b"
JUDGE_MODEL = "openai/gpt-oss-20b"


writer_llm = ChatGroq(
    model=WRITER_MODEL,
    temperature=0.3,
    max_tokens=8192,
)

judge_llm = ChatGroq(
    model=JUDGE_MODEL,
    temperature=0,
    max_tokens=4096,
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
- Copy numbers, ratings and dates exactly as written in the source. Never round or convert them.
- In the source text, "[...]" separates unrelated excerpts, possibly from different people. Never combine two excerpts into one person's opinion.
- Attribute opinions to their source ("One MyAnimeList reviewer says...", "CBR argues..."). Do not state opinions as facts.
- Do not make claims about groups of people (fans, audiences). If a source's meaning is unclear or sensitive, leave it out.
- Each bullet states ONE fact and cites only the sources that directly support it.
- Under "If you liked this, try", list a title ONLY if a source explicitly recommends it as similar to this title. A title that merely appears in a comparison or list does not count. If no source does, write "Not enough info found.
- Cite with plain square brackets exactly like [S3]. Never use 【S3】, (S3) or [S3, S4].
- Use plain "## Heading" lines. No bold on headings.
- Only write "critics" or "fans" when a source names several; otherwise say "one reviewer" or "one writer".
- A claim about a band or artist is not a claim about this title unless the source names this title.
- Never use relative time ("twenty years ago", "recently", "currently"). Use an explicit year from the source, or leave it out.
- Never copy table formatting like "StarStarStar". Combine ratings into one bullet in plain words, or skip them.
- If a quote is about a different work (a previous album, season or film), do not use it.
- Never write notes about the sources or about missing information inside a bullet. If a fact is incomplete, leave it out.
- "What divides people" needs an explicit disagreement stated in a source. Review scores alone do not count. Otherwise write "Not enough info found."
- Never add details that no source states. Stay at or below the strength of what the source says."""

JUDGE_PROMPT = """You are a spoiler checker.

PREMISE = what the official synopsis or first episode establishes. Allowed.
SPOILER = any event, twist, death, reveal or outcome after the premise. Not allowed.
Also flag any line that describes specific villains or antagonists, battles, arcs, episodes, or events from later seasons.

Brief to check:
{report}

List every line that contains a spoiler or flagged item, with a one-line reason.
If there are none, reply exactly: NONE"""


CLAIM_PROMPT = """You verify one claim against source text.

CLAIM: {claim}

SOURCE TEXT:
{evidence}

Check all three:
1. Is the claim stated in the source text?
2. Is it about the SAME subject (same album, show, season or person) as the source passage? A quote about a different work is UNSUPPORTED.
3. Is the strength matched? One person does not support "reviewers" or "critics". "Many" does not support "countless".

Note: "[...]" separates unrelated excerpts. Facts from different excerpts do not come from the same person.

Reply with one word on the first line: SUPPORTED, PARTIAL or UNSUPPORTED.
On the second line, one short sentence explaining why."""


def format_sources(sources: list[dict]) -> str:
    return "\n\n".join(f"[{s['id']}] {source_text(s)}" for s in sources)


def normalize_citations(report: str) -> str:
    report = report.replace("【", "[").replace("】", "]")

    def split(m):  # "[S2, S5]" -> "[S2][S5]"
        return "".join(f"[{i}]" for i in re.findall(r"S\d+", m.group(0)))

    report = re.sub(r"\[(?:S\d+\s*[,;]\s*)+S\d+\]", split, report)
    report = re.sub(r"^\*\*(#{1,3} .*?)\*\*\s*$", r"\1", report, flags=re.MULTILINE)
    return report


def write_node(state: ResearchState) -> dict:
    prompt = WRITE_PROMPT.format(
        title=state["question"], sources=format_sources(state["sources"])
    )
    feedback = state.get("spoiler_check", "")
    if feedback and not feedback.strip().upper().startswith("NONE"):
        prompt += (
            "\n\nYour previous draft was rejected because it contains spoilers:\n"
            f"{feedback}\n\nPrevious draft:\n{state['report']}\n\n"
            "Rewrite the full brief and remove every spoiler listed above."
        )
    reply = writer_llm.invoke(prompt)

    report = normalize_citations(reply.content)
    if not re.search(r"\[S\d+\]", report):
        raise ValueError(
            "No recognizable citations in the draft. The checks would pass without checking anything."
        )
    return {"report": report, "revisions": state.get("revisions", 0) + 1}


def ask(llm, prompt: str) -> str:
    text = (llm.invoke(prompt).content or "").strip()
    if not text:
        raise ValueError(
            "Model returned empty content (reasoning may have used the whole token budget)."
        )
    return text


def check_citations(report: str, sources: list[dict]):
    valid = {s["id"] for s in sources}
    used = set(re.findall(r"\[(S\d+)\]", report))
    return used, used - valid


def judge_spoilers(report: str) -> str:
    return ask(judge_llm, JUDGE_PROMPT.format(report=report))


def check_numbers(report: str, sources: list[dict]) -> list[str]:
    seen = " ".join(source_text(s) for s in sources)
    body = re.sub(r"\[S\d+\]", "", report)
    nums = set(re.findall(r"\d+(?:\.\d+)?", body))
    return sorted(
        n for n in nums if not re.search(rf"(?<![\d.]){re.escape(n)}(?!\d)", seen)
    )


def check_claims(report: str, sources: list[dict]) -> list[tuple[str, str]]:
    by_id = {s["id"]: s for s in sources}
    problems = []
    for line in report.splitlines():
        ids = re.findall(r"\[(S\d+)\]", line)
        if not ids or line.lstrip().startswith("#"):
            continue
        claim = re.sub(r"\[S\d+\]", "", line).strip("-• ").strip()
        evidence = "\n\n".join(source_text(by_id[i]) for i in ids if i in by_id)
        verdict = ask(judge_llm, CLAIM_PROMPT.format(claim=claim, evidence=evidence))

        if not verdict.upper().startswith("SUPPORTED"):
            problems.append((claim[:90], verdict))
    return problems


def clean_stars(text: str) -> str:
    def repl(m):
        raw = m.group(0)
        n = raw.count("Star")
        return f"{n}.5 stars" if "Half" in raw else f"{n} stars"

    return re.sub(r"(?:Star){2,}(?:Half star)?|(?:Star)+Half star", repl, text)


def source_text(s: dict) -> str:
    return clean_stars(f"{s['title']}\n{s['snippet'][:600]}")


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
