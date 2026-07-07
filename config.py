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
    ],
    "AI Research Papers": [
        "http://arxiv.org/rss/cs.AI",
        "http://arxiv.org/rss/cs.LG",
        "http://arxiv.org/rss/cs.CL",
    ],
    "MLOps & AI Engineering": [
        "https://mlops.community/feed/",
        "https://towardsdatascience.com/feed",
    ],
    "GenAI Tools & Products": [
        "https://www.deeplearning.ai/the-batch/feed/",
    ],
}

# SEARCH SETTINGS

TAVILY_MAX_RESULTS = 5      # articles per topic per Tavily search
RSS_MAX_RESULTS    = 3      # articles per feed (most recent N entries)


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