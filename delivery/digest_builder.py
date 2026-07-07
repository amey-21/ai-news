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
    Build a polished, email-safe HTML digest from summarized articles.

    Args:
        articles: List of summarized article dicts
        date_str: Human-readable date string e.g. "July 6, 2026"

    Returns:
        Complete HTML string ready to send as email body.
    """

    grouped = group_by_topic(articles)
    topic_sections_html = ""

    topic_colors = {
        "LLMs & Foundation Models": ("#7c3aed", "#f5f3ff"),
        "MLOps & AI Engineering": ("#2563eb", "#eff6ff"),
        "AI Research Papers": ("#0891b2", "#ecfeff"),
        "Indian AI Ecosystem": ("#ea580c", "#fff7ed"),
        "GenAI Tools & Products": ("#db2777", "#fdf2f8"),
        "AI Jobs & Career": ("#16a34a", "#f0fdf4"),
    }

    for topic, topic_articles in grouped.items():
        icon = TOPIC_ICONS.get(topic, "📌")
        accent, tint = topic_colors.get(topic, ("#4f46e5", "#eef2ff"))

        articles_html = ""
        for index, article in enumerate(topic_articles, start=1):
            title = article["title"][:90] + "..." if len(article["title"]) > 90 else article["title"]

            articles_html += f"""
            <div style="
                background: #ffffff;
                border: 1px solid #e8eaf0;
                border-left: 4px solid {accent};
                border-radius: 14px;
                padding: 20px 22px;
                margin-bottom: 14px;
                box-shadow: 0 6px 20px rgba(15, 23, 42, 0.06);
            ">
                <div style="
                    font-size: 11px;
                    font-weight: 800;
                    color: {accent};
                    letter-spacing: 0.08em;
                    text-transform: uppercase;
                    margin-bottom: 9px;
                ">
                    Story {index:02d}
                </div>

                <div style="
                    font-size: 17px;
                    font-weight: 750;
                    color: #0f172a;
                    margin-bottom: 10px;
                    line-height: 1.45;
                ">
                    {title}
                </div>

                <div style="
                    font-size: 14px;
                    color: #475569;
                    line-height: 1.75;
                    margin-bottom: 16px;
                ">
                    {article['summary']}
                </div>

                <a href="{article['url']}" style="
                    display: inline-block;
                    background: {tint};
                    border: 1px solid {accent}22;
                    border-radius: 999px;
                    padding: 9px 14px;
                    font-size: 13px;
                    color: {accent};
                    text-decoration: none;
                    font-weight: 700;
                ">Read full story&nbsp; →</a>
            </div>
            """

        topic_sections_html += f"""
        <div style="margin-bottom: 38px;">
            <div style="
                background: {tint};
                border: 1px solid {accent}22;
                border-radius: 14px;
                padding: 14px 16px;
                margin-bottom: 16px;
            ">
                <table role="presentation" width="100%" cellspacing="0" cellpadding="0" border="0">
                    <tr>
                        <td style="
                            font-size: 18px;
                            font-weight: 800;
                            color: #0f172a;
                            line-height: 1.3;
                        ">
                            <span style="margin-right: 7px;">{icon}</span>{topic}
                        </td>
                        <td align="right" style="
                            font-size: 12px;
                            font-weight: 700;
                            color: {accent};
                            white-space: nowrap;
                        ">
                            {len(topic_articles)} STORIES
                        </td>
                    </tr>
                </table>
            </div>
            {articles_html}
        </div>
        """

    total_articles = len(articles)
    total_topics = len(grouped)

    html = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <meta name="color-scheme" content="light">
        <title>AI Digest — {date_str}</title>
    </head>

    <body style="
        margin: 0;
        padding: 0;
        background-color: #eef2f7;
        font-family: Inter, -apple-system, BlinkMacSystemFont, 'Segoe UI', Arial, sans-serif;
        color: #0f172a;
    ">
        <div style="
            display: none;
            max-height: 0;
            overflow: hidden;
            opacity: 0;
            color: transparent;
        ">
            {total_articles} AI stories across {total_topics} topics — curated for you.
        </div>

        <div style="padding: 28px 12px;">
            <div style="
                max-width: 680px;
                margin: 0 auto;
                background: #f8fafc;
                border: 1px solid #e2e8f0;
                border-radius: 22px;
                overflow: hidden;
                box-shadow: 0 18px 50px rgba(15, 23, 42, 0.10);
            ">

                <!-- HERO -->
                <div style="
                    background: linear-gradient(135deg, #111827 0%, #312e81 52%, #2563eb 100%);
                    padding: 42px 34px 34px;
                    text-align: left;
                ">
                    <div style="
                        display: inline-block;
                        background: rgba(255,255,255,0.12);
                        border: 1px solid rgba(255,255,255,0.18);
                        border-radius: 999px;
                        padding: 7px 11px;
                        font-size: 11px;
                        font-weight: 800;
                        color: #dbeafe;
                        letter-spacing: 0.09em;
                        text-transform: uppercase;
                        margin-bottom: 18px;
                    ">
                        ✦ Your curated AI briefing
                    </div>

                    <div style="
                        font-size: 34px;
                        font-weight: 850;
                        color: #ffffff;
                        letter-spacing: -0.04em;
                        line-height: 1.08;
                        margin-bottom: 10px;
                    ">
                        AI Digest<span style="color: #93c5fd;">.</span>
                    </div>

                    <div style="
                        font-size: 15px;
                        color: #cbd5e1;
                        line-height: 1.6;
                        margin-bottom: 24px;
                    ">
                        The signal in AI, minus the noise.<br>
                        <span style="color: #93c5fd;">{date_str}</span>
                    </div>

                    <table role="presentation" cellspacing="0" cellpadding="0" border="0">
                        <tr>
                            <td style="
                                background: rgba(255,255,255,0.10);
                                border-radius: 12px;
                                padding: 11px 16px;
                                color: #ffffff;
                                font-size: 13px;
                                font-weight: 700;
                            ">
                                <span style="font-size: 20px;">{total_articles}</span><br>
                                <span style="color: #bfdbfe; font-size: 11px; text-transform: uppercase; letter-spacing: 0.06em;">Stories</span>
                            </td>
                            <td width="10"></td>
                            <td style="
                                background: rgba(255,255,255,0.10);
                                border-radius: 12px;
                                padding: 11px 16px;
                                color: #ffffff;
                                font-size: 13px;
                                font-weight: 700;
                            ">
                                <span style="font-size: 20px;">{total_topics}</span><br>
                                <span style="color: #bfdbfe; font-size: 11px; text-transform: uppercase; letter-spacing: 0.06em;">Topics</span>
                            </td>
                        </tr>
                    </table>
                </div>

                <!-- CONTENT -->
                <div style="padding: 34px 28px 10px;">
                    <div style="
                        font-size: 12px;
                        font-weight: 800;
                        color: #64748b;
                        letter-spacing: 0.09em;
                        text-transform: uppercase;
                        margin-bottom: 24px;
                    ">
                        Today's intelligence
                    </div>

                    {topic_sections_html}
                </div>

                <!-- FOOTER -->
                <div style="
                    background: #0f172a;
                    padding: 28px 24px;
                    text-align: center;
                ">
                    <div style="
                        font-size: 18px;
                        font-weight: 800;
                        color: #ffffff;
                        margin-bottom: 7px;
                    ">
                        Stay curious. Stay ahead.
                    </div>
                    <div style="
                        font-size: 12px;
                        color: #94a3b8;
                        line-height: 1.7;
                    ">
                        AI Digest · Delivered every 3 days<br>
                        Built with Python + OpenAI
                    </div>
                </div>

            </div>

            <div style="
                max-width: 680px;
                margin: 14px auto 0;
                text-align: center;
                font-size: 11px;
                color: #94a3b8;
            ">
                Curated intelligence for builders, researchers, and AI enthusiasts.
            </div>
        </div>
    </body>
    </html>
    """

    return html

