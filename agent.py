# agent.py — updated with Milestone 4

from datetime import datetime
from search.tavily_searcher import fetch_tavily_articles
from search.rss_fetcher import fetch_rss_articles
from search.arxiv_searcher import fetch_arxiv_articles
from synthesis.summarizer import summarize_all
from delivery.digest_builder import build_digest_html
from delivery.email_sender import send_digest
from config import TOPICS, ARTICLES_PER_TOPIC


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
        arxiv_articles  = fetch_arxiv_articles(topic)
        topic_articles = tavily_articles + rss_articles + arxiv_articles

        # Deduplicate within this topic
        unique_topic_articles = deduplicate(topic_articles)
        # Sort by score descending (higher is more relevant)
        unique_topic_articles.sort(key=lambda x: x.get('score', 0.0), reverse=True)
        # Limit to articles per topic
        limited_topic_articles = unique_topic_articles[:ARTICLES_PER_TOPIC]
        all_articles.extend(limited_topic_articles)
        print(f"[Topic: {topic}] Fetched: {len(topic_articles)} -> After dedup: {len(unique_topic_articles)} -> Limited to {ARTICLES_PER_TOPIC}: {len(limited_topic_articles)}")

    print(f"\n[Agent] Total articles collected: {len(all_articles)} ({len(TOPICS)} topics x {ARTICLES_PER_TOPIC} articles each)")
    return all_articles


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