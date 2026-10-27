import os
from dotenv import load_dotenv
from tavily import TavilyClient
from plan import ResearchState, plan_node

load_dotenv()
tavily = TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))

EXCLUDE = ["facebook.com", "tiktok.com", "youtube.com", "instagram.com"]


def search_node(state: ResearchState) -> dict:
    seen_urls = set()
    sources = []

    for query in state["queries"]:
        try:
            response = tavily.search(
                query=query, max_results=3, exclude_domains=EXCLUDE
            )
        except Exception as e:
            print(f"search failed for {query!r}: {e}")
            continue
        for r in response["results"]:
            if r["url"] in seen_urls:
                continue
            seen_urls.add(r["url"])
            sources.append(
                {
                    "id": f"S{len(sources) + 1}",
                    "title": r["title"],
                    "url": r["url"],
                    "snippet": r["content"],
                    "query": query,
                }
            )
    return {"sources": sources}


if __name__ == "__main__":
    state = {"question": "Frieren: Beyond Journey's End"}
    state.update(plan_node(state))
    state.update(search_node(state))

    for s in state["sources"]:
        print(s["id"], "-", s["title"])
        print("   ", s["url"])
        print("   ", s["snippet"][:150].replace("\n", " "))
