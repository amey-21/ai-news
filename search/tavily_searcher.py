# search/tavily_searcher.py

import os
from tavily import TavilyClient
from dotenv import load_dotenv
from config import TAVILY_QUERIES, TAVILY_MAX_RESULTS

load_dotenv()   # reads .env file and loads TAVILY_API_KEY into environment


def fetch_tavily_articles(topic: str) -> list[dict]:
    """
    Search Tavily for recent articles on a given topic.

    Args:
        topic: One of the topic strings defined in config.TOPICS

    Returns:
        List of article dicts, each with keys:
        { topic, title, url, content, source }

    Returns empty list if topic has no query defined, or if API call fails.
    """

    # Step 1: Check if this topic has a query defined
    # Some topics may only use RSS no Tavily query needed
    query = TAVILY_QUERIES.get(topic)
    if not query:
        print(f"[Tavily] No query configured for topic: {topic}. Skipping.")
        return []

    # Step 2: Initialize Tavily client with API key from environment
    # We never hardcode API keys in source code always from environment
    api_key = os.getenv("TAVILY_API_KEY")
    if not api_key:
        raise EnvironmentError("TAVILY_API_KEY not found in environment. Check your .env file.")

    client = TavilyClient(api_key=api_key)

    # Step 3: Call the Tavily search API
    try:
        response = client.search(
            query=query,
            max_results=TAVILY_MAX_RESULTS,
            include_raw_content=False,   # summary content is enough, saves tokens
            search_depth="advanced",     # deeper search, better quality results
        )
    except Exception as e:
        # We catch ALL exceptions here deliberately.
        # If Tavily is down or rate-limited, we don't want the entire
        # agent to crash. We log the error and return empty — the RSS
        # fetcher can still provide articles for this topic.
        print(f"[Tavily] Search failed for topic '{topic}': {e}")
        return []

    # Step 4: Parse the response into our standard article dict format
    # This is the "contract" shape the rest of the system expects
    articles = []
    for result in response.get("results", []):
        articles.append({
            "topic":   topic,
            "title":   result.get("title", "No title"),
            "url":     result.get("url", ""),
            "content": result.get("content", ""),   # Tavily-extracted clean text
            "source":  "tavily",
        })

    print(f"[Tavily] Fetched {len(articles)} articles for topic: {topic}")
    return articles