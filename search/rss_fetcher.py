# search/rss_fetcher.py

import feedparser
from config import RSS_FEEDS, RSS_MAX_RESULTS
from datetime import datetime, timezone


def fetch_rss_articles(topic: str) -> list[dict]:
    """
    Fetch recent articles from RSS feeds for a given topic.

    Args:
        topic: One of the topic strings defined in config.TOPICS

    Returns:
        List of article dicts with keys: { topic, title, url, content, source }
        Returns empty list if topic has no feeds configured.
    """

    # Step 1: Check if this topic has RSS feeds configured
    feeds = RSS_FEEDS.get(topic, [])
    if not feeds:
        print(f"[RSS] No feeds configured for topic: {topic}. Skipping.")
        return []

    articles = []

    # Step 2: Loop over each feed URL for this topic
    for feed_url in feeds:
        try:
            # feedparser.parse() fetches the URL and parses the XML
            # It handles malformed XML, redirects, and encoding issues
            parsed = feedparser.parse(feed_url)

            # Step 3: Extract the most recent N entries from this feed
            # parsed.entries is a list of items, newest first
            for entry in parsed.entries[:RSS_MAX_RESULTS]:

                # Step 4: Extract content — RSS entries have varying structures
                # Some feeds use 'summary', others use 'content', others use 'description'
                # We try each in order of preference
                content = (
                    entry.get("summary", "")
                    or entry.get("description", "")
                    or entry.get("title", "")
                )

                articles.append({
                    "topic":   topic,
                    "title":   entry.get("title", "No title"),
                    "url":     entry.get("link", ""),
                    "content": content,
                    "source":  "rss",
                })

        except Exception as e:
            # Same defensive pattern as Tavily — one broken feed
            # should not stop us from reading all other feeds
            print(f"[RSS] Failed to fetch feed {feed_url}: {e}")
            continue

    print(f"[RSS] Fetched {len(articles)} articles for topic: {topic}")
    return articles