# delivery/digest_builder.py

from config import TOPICS


# ---------------------------------------------------------------------------
# GROUPING
# ---------------------------------------------------------------------------

def group_by_topic(articles: list[dict]) -> dict[str, list[dict]]:
    """
    Transform flat list of article dicts into a dict grouped by topic.

    Only topics that have at least one article appear in the output.
    Empty topics are silently dropped — no empty sections in the digest.

    Args:
        articles: List of summarized article dicts

    Returns:
        Dict mapping topic string to list of articles for that topic.
        Order of topics matches TOPICS config (not insertion order).
    """
    # Step 1: Build grouped dict from flat list
    grouped = {}
    for article in articles:
        topic = article["topic"]
        if topic not in grouped:
            grouped[topic] = []
        grouped[topic].append(article)

    # Step 2: Re-order to match TOPICS config order
    # Why? Our grouping dict has topics in the order articles were
    # appended — which depends on search timing, not our intended order.
    # We want LLMs first, MLOps second, etc. — as defined in config.
    ordered = {}
    for topic in TOPICS:
        if topic in grouped:
            ordered[topic] = grouped[topic]

    return ordered


# ---------------------------------------------------------------------------
# TOPIC ICONS
# One emoji per topic — makes sections visually scannable in email
# ---------------------------------------------------------------------------

TOPIC_ICONS = {
    "LLMs & Foundation Models":  "🧠",
    "MLOps & AI Engineering":    "⚙️",
    "AI Research Papers":        "📄",
    "Indian AI Ecosystem":       "🇮🇳",
    "GenAI Tools & Products":    "🛠️",
    "AI Jobs & Career":          "💼",
}


# ---------------------------------------------------------------------------
# HTML BUILDER
# ---------------------------------------------------------------------------

def build_digest_html(articles: list[dict], date_str: str) -> str:
    """
    Build a complete HTML email digest from summarized articles.

    Args:
        articles: List of summarized article dicts
        date_str: Human-readable date string e.g. "July 6, 2026"

    Returns:
        Complete HTML string ready to send as email body.
    """

    grouped = group_by_topic(articles)

    # Step 1: Build each topic section as an HTML string
    topic_sections_html = ""
    for topic, topic_articles in grouped.items():
        icon = TOPIC_ICONS.get(topic, "📌")

        # Build article cards for this topic
        articles_html = ""
        for article in topic_articles:
            articles_html += f"""
            <div style="
                background: #ffffff;
                border: 1px solid #e5e7eb;
                border-radius: 8px;
                padding: 16px 20px;
                margin-bottom: 12px;
            ">
                <div style="
                    font-size: 15px;
                    font-weight: 600;
                    color: #111827;
                    margin-bottom: 8px;
                    line-height: 1.4;
                ">
                    {article['title'][:80] + '...' if len(article['title']) > 80 else article['title']}
                </div>
                <div style="
                    font-size: 14px;
                    color: #374151;
                    line-height: 1.6;
                    margin-bottom: 12px;
                ">
                    {article['summary']}
                </div>
                <a href="{article['url']}" style="
                    display: inline-block;
                    font-size: 13px;
                    color: #2563eb;
                    text-decoration: none;
                    font-weight: 500;
                ">Read more →</a>
            </div>
            """

        # Wrap articles in a topic section
        topic_sections_html += f"""
        <div style="margin-bottom: 32px;">
            <div style="
                font-size: 18px;
                font-weight: 700;
                color: #111827;
                margin-bottom: 16px;
                padding-bottom: 8px;
                border-bottom: 2px solid #e5e7eb;
            ">
                {icon} {topic} {len(grouped[topic])} articles
            </div>
            {articles_html}
        </div>
        """

    # Step 2: Wrap everything in the outer email shell
    total_articles = len(articles)
    total_topics   = len(grouped)

    html = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>AI Digest — {date_str}</title>
    </head>
    <body style="
        margin: 0;
        padding: 0;
        background-color: #f3f4f6;
        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
    ">
        <div style="
            max-width: 640px;
            margin: 0 auto;
            padding: 24px 16px;
        ">

            <!-- HEADER -->
            <div style="
                background: linear-gradient(135deg, #1e3a5f 0%, #2563eb 100%);
                border-radius: 12px;
                padding: 28px 32px;
                margin-bottom: 24px;
                text-align: center;
            ">
                <div style="
                    font-size: 24px;
                    font-weight: 700;
                    color: #ffffff;
                    margin-bottom: 6px;
                ">
                    🤖 AI Digest
                </div>
                <div style="font-size: 14px; color: #bfdbfe;">
                    {date_str}
                </div>
                <div style="
                    font-size: 13px;
                    color: #93c5fd;
                    margin-top: 8px;
                ">
                    {total_articles} articles across {total_topics} topics
                </div>
            </div>

            <!-- TOPIC SECTIONS -->
            {topic_sections_html}

            <!-- FOOTER -->
            <div style="
                text-align: center;
                padding: 20px;
                font-size: 12px;
                color: #9ca3af;
                border-top: 1px solid #e5e7eb;
                margin-top: 16px;
            ">
                AI Digest · Delivered every 3 days · Built with Python + Openai
            </div>

        </div>
    </body>
    </html>
    """

    return html