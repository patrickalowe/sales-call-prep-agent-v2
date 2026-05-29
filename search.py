"""
Live web research via the Tavily search API (https://tavily.com).

This replaces Claude's server-side web search. Instead of letting the model
search on its own (which pulls whole pages into the prompt and runs up tokens),
we run the search ourselves here, trim the results, and hand only a compact
summary to Claude. That keeps token usage low and gives us full control over
how many searches run and how much content comes back.

The search provider is isolated in this one file on purpose: to swap Tavily for
another engine later, you only change search_web().

Requires TAVILY_API_KEY in the environment (loaded from .env). Get a key at
https://app.tavily.com — the free tier covers plenty of testing.
"""

import os

from tavily import TavilyClient

# Cap each result snippet so the context handed to Claude stays small. Tavily
# can return long page extracts; we only need enough to summarize from.
_MAX_SNIPPET_CHARS = 500


def search_web(query, max_results=5):
    """Run one Tavily search and return a compact, model-ready text block.

    Returns a string: a short engine summary (if any) followed by the top
    results as "- title (url): snippet" lines. Raises RuntimeError with a
    clear message if the API key is missing.
    """
    if not os.environ.get("TAVILY_API_KEY"):
        raise RuntimeError(
            "TAVILY_API_KEY is not set. Add it to your .env file "
            "(get a key at https://app.tavily.com), or run with --no-search."
        )

    client = TavilyClient()  # reads TAVILY_API_KEY from the environment
    response = client.search(
        query=query,
        max_results=max_results,
        search_depth="basic",   # "basic" = 1 credit; "advanced" costs more
        include_answer=True,    # a one-paragraph synthesized summary
    )

    return _format_results(response)


def _format_results(response):
    """Turn a Tavily response dict into a compact text block for the prompt."""
    parts = []

    answer = response.get("answer")
    if answer:
        parts.append(f"Search summary: {answer}")

    for result in response.get("results", []):
        title = result.get("title", "").strip()
        url = result.get("url", "").strip()
        snippet = (result.get("content", "") or "").strip()[:_MAX_SNIPPET_CHARS]
        parts.append(f"- {title} ({url}): {snippet}")

    return "\n".join(parts) if parts else "No search results were found."
