# TOPIC CONFIGURATION


TOPICS = [
    "LLMs & Foundation Models",
    "MLOps & AI Engineering",
    "AI Research Papers",
    "Indian AI Ecosystem",
    "GenAI Tools & Products",
    "AI Jobs & Career",
]


# TAVILY SEARCH QUERIES

TAVILY_QUERIES = {
    "LLMs & Foundation Models":  "large language models foundation models news 2026",
    "MLOps & AI Engineering":    "MLOps LLMOps AI engineering production deployment 2026",
    "AI Research Papers":        "AI machine learning research paper breakthrough arxiv 2026",
    "Indian AI Ecosystem":       "India AI startup funding government policy 2026",
    "GenAI Tools & Products":    "generative AI tools product launch announcement 2026",
    "AI Jobs & Career":          "AI engineer jobs hiring market salary trends 2026",
}

# RSS FEEDS

RSS_FEEDS = {
    "LLMs & Foundation Models": [
        "https://huggingface.co/blog/feed.xml",
        "https://openai.com/blog/rss.xml",
        "https://www.anthropic.com/news/rss",
        "https://ai.googleblog.com/atom/",
        "https://ai.meta.com/blog/feed/",
        "https://deepmind.com/blog/feed.xml",
    ],
    "AI Research Papers": [
        "http://arxiv.org/rss/cs.AI",
        "http://arxiv.org/rss/cs.LG",
        "http://arxiv.org/rss/cs.CL",
        "http://arxiv.org/rss/cs.CV",
        "http://arxiv.org/rss/stat.ML",
    ],
    "MLOps & AI Engineering": [
        "https://mlops.community/feed/",
        "https://towardsdatascience.com/feed",
        "https://aws.amazon.com/blogs/machine-learning/feed/",
        "https://databricks.com/blog/feed/",
        "https://cloud.google.com/blog/topics/ai/rss",
    ],
    "GenAI Tools & Products": [
        "https://www.deeplearning.ai/the-batch/feed/",
        "https://www.producthunt.com/feed?category=ai-and-ml",
        "https://therelease.org/feed/",
    ],
    "Indian AI Ecosystem": [
        "https://analyticsindiamag.com/feed/",
        "https://inc42.com/feed/",
        "https://yourstory.com/feed/tag/ai/",
    ],
    "AI Jobs & Career": [
        # Few reliable AI-specific job RSS feeds; leave empty for now
    ],
}

# SEARCH SETTINGS

TAVILY_MAX_RESULTS = 5      # articles per topic per Tavily search
RSS_MAX_RESULTS    = 3      # articles per feed (most recent N entries)
ARXIV_MAX_RESULTS  = 3      # articles per topic from ArXiv API


# LLM CONFIGURATION


LLM_PROVIDER    = "openai"                    

LLM_CONFIG = {
    "openai": {
        "base_url": "https://api.openai.com/v1",
        "model":    "gpt-4o-mini",
        "api_key_env": "OPENAI_API_KEY",
    },
}

# SUMMARIZATION SETTINGS


BATCH_SIZE          = 10      # articles processed in parallel per batch
BATCH_DELAY_SECONDS = 0.5     # sleep between batches to respect rate limits
MAX_SUMMARY_TOKENS  = 200     # keep summaries short — 3 sentences max
ARTICLES_PER_TOPIC  = 5       # number of articles to include per topic section (3-5 recommended)