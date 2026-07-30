# search/arxiv_searcher.py

import feedparser
from config import ARXIV_MAX_RESULTS
import time


def fetch_arxiv_articles(topic: str) -> list[dict]:
    """
    Search ArXiv for recent articles on a given topic.

    Args:
        topic: One of the topic strings defined in config.TOPICS

    Returns:
        List of article dicts, each with keys:
        { topic, title, url, content, source, score }
        where content is the arXiv abstract, source is 'arxiv',
        and score is a recency-based score (0-1).
    """
    # Build the ArXiv API query URL
    # Format: http://export.arxiv.org/api/query?search_query=all:{topic}&start=0&max_results={N}&sortBy=submittedDate&sortOrder=descending
    query_str = topic.replace(" ", "+")  # ArXiv API expects spaces as + or %20
    url = f'http://export.arxiv.org/api/query?search_query=all:{query_str}&start=0&max_results={ARXIV_MAX_RESULTS}&sortBy=submittedDate&sortOrder=descending'

    try:
        # Fetch and parse the ArXiv API response
        feed = feedparser.parse(url)

        # Check if we got a valid response
        if feed.bozo:
            print(f"[ArXiv] Failed to parse feed for topic '{topic}': {feed.bozo_exception}")
            return []

    except Exception as e:
        print(f"[ArXiv] Search failed for topic '{topic}': {e}")
        return []

    articles = []
    current_time = time.time()
    max_age_seconds = 30 * 24 * 60 * 60  # 30 days for full recency score

    for entry in feed.entries:
        # Extract title
        title = entry.get('title', 'No title').replace("\n", " ").strip()

        # Extract URL (use the first link that isn't the PDF link, or the entry ID)
        url = entry.get('id', '')  # ArXiv entry ID like http://arxiv.org/abs/2103.00001v1

        # Extract content (summary/abstract)
        content = entry.get('summary', 'No summary available').replace("\n", " ").strip()

        # Extract published date
        published = entry.get('published_parsed')
        if published:
            # published is a time.struct_time in UTC
            published_timestamp = time.mktime(published)
        else:
            # fallback to current time if no date
            published_timestamp = current_time

        # Calculate recency score (newer = higher score)
        age_seconds = current_time - published_timestamp
        recency_score = max(0.0, 1.0 - (age_seconds / max_age_seconds))

        articles.append({
            "topic":   topic,
            "title":   title,
            "url":     url,
            "content": content,
            "source":  "arxiv",
            "score":   recency_score,
        })

    print(f"[ArXiv] Fetched {len(articles)} articles for topic: {topic}")
    return articles