# agent.py — updated with Milestone 4

from datetime import datetime
from search.tavily_searcher import fetch_tavily_articles
from search.rss_fetcher import fetch_rss_articles
from synthesis.summarizer import summarize_all
from delivery.digest_builder import build_digest_html
from delivery.email_sender import send_digest
from config import TOPICS


def deduplicate(articles: list[dict]) -> list[dict]:
    seen_urls = set()
    unique = []
    for article in articles:
        url = article["url"]
        if url and url not in seen_urls:
            seen_urls.add(url)
            unique.append(article)
    return unique


def fetch_all_articles() -> list[dict]:
    all_articles = []
    for topic in TOPICS:
        print(f"\n{'='*50}")
        print(f"Fetching: {topic}")
        print(f"{'='*50}")
        tavily_articles = fetch_tavily_articles(topic)
        rss_articles    = fetch_rss_articles(topic)
        all_articles.extend(tavily_articles + rss_articles)

    unique_articles = deduplicate(all_articles)
    print(f"\n[Agent] Total: {len(all_articles)} → After dedup: {len(unique_articles)}")
    return unique_articles


if __name__ == "__main__":
    # Milestone 1: Fetch
    articles = fetch_all_articles()

    # Milestone 2: Summarize
    summaries = summarize_all(articles)

    # Milestone 3: Build digest
    date_str = datetime.now().strftime("%B %d, %Y")
    html     = build_digest_html(summaries, date_str)

    # Save preview (keep this even after wiring email — useful for debugging)
    with open("digest_preview.html", "w", encoding="utf-8") as f:
        f.write(html)
    print(f"[Agent] Preview saved to digest_preview.html")

    # Milestone 4: Send email
    send_digest(html, summaries, date_str)