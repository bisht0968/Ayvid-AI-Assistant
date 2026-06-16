from duckduckgo_search import DDGS


def search_web(query: str, max_results: int = 3) -> list:
    results = []
    try:
        with DDGS() as ddgs:
            for result in ddgs.text(query, max_results=max_results):
                results.append({
                    "title": result.get("title", ""),
                    "url": result.get("href", ""),
                    "snippet": result.get("body", "")
                })
    except Exception as e:
        print(f"[Search error] {e}")
    return results