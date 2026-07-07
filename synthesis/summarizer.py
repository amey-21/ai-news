# synthesis/summarizer.py

import os
import asyncio
from openai import AsyncOpenAI
from dotenv import load_dotenv
from config import (
    LLM_PROVIDER,
    LLM_CONFIG,
    BATCH_SIZE,
    BATCH_DELAY_SECONDS,
    MAX_SUMMARY_TOKENS,
)

load_dotenv()


# ---------------------------------------------------------------------------
# LLM CLIENT SETUP
# ---------------------------------------------------------------------------

def build_llm_client() -> AsyncOpenAI:
    """
    Build an async OpenAI-compatible client based on LLM_PROVIDER in config.

    Returns an AsyncOpenAI client pointed at the correct base_url
    with the correct API key loaded from environment.

    Why AsyncOpenAI and not OpenAI?
    AsyncOpenAI supports 'await client.chat.completions.create(...)'
    which is required for our batched parallel execution pattern.
    The regular OpenAI client is synchronous — it blocks.
    """
    provider_config = LLM_CONFIG[LLM_PROVIDER]

    api_key = os.getenv(provider_config["api_key_env"])
    if not api_key:
        raise EnvironmentError(
            f"API key not found. Expected env var: {provider_config['api_key_env']}"
        )

    return AsyncOpenAI(
        api_key=api_key,
        base_url=provider_config["base_url"],
    )


# Build once at module load time — reused across all summarization calls.
# Creating a new client per article would be wasteful (connection overhead).
client = build_llm_client()


# ---------------------------------------------------------------------------
# SYSTEM PROMPT
# ---------------------------------------------------------------------------

SYSTEM_PROMPT = """You are an AI research digest assistant.
Your job is to summarize AI news articles for a busy ML engineer.

Rules:
- Write exactly 1 sentence
- Be specific. Use technical terms where appropriate.
- Never write vague summaries like "This is an interesting development."
- Never start with "This article..." or "The article discusses..."

Be specific. Use technical terms where appropriate.
Never write vague summaries like "This is an interesting development."
Never start with "This article..." or "The article discusses..."
"""


# ---------------------------------------------------------------------------
# SINGLE ARTICLE SUMMARIZATION
# ---------------------------------------------------------------------------

async def summarize_article(article: dict) -> dict:
    """
    Summarize a single article using the configured LLM.

    Args:
        article: Dict with keys: topic, title, url, content, source

    Returns:
        Same dict with 'content' replaced by 'summary'.
        If summarization fails, 'summary' contains a fallback message
        so the article still appears in the digest (graceful degradation).

    Why async?
    This function will be called concurrently via asyncio.gather().
    The 'await' on the API call yields control while waiting for
    the network response — allowing other summarize_article() calls
    to run simultaneously.
    """

    # Build the user prompt — include title for context
    # Content may be long; the LLM will compress it
    user_prompt = f"""Article Title: {article['title']}

Article Content:
{article['content'][:2000]}

Write exactly 1-sentence short summary following the rules."""

    # Why [:2000]?
    # Some articles have very long content. We truncate to 2000 chars
    # to control token usage. The title + first 2000 chars contains
    # the key information in virtually all news articles.

    try:
        response = await client.chat.completions.create(
            model=LLM_CONFIG[LLM_PROVIDER]["model"],
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user",   "content": user_prompt},
            ],
            max_tokens=MAX_SUMMARY_TOKENS,
            temperature=0.3,    
        )

        summary = response.choices[0].message.content.strip()
    
    except Exception as e:
        # Graceful degradation — if one article fails to summarize,
        # we don't crash the whole digest. We use a fallback summary.
        print(f"[Summarizer] Failed to summarize '{article['title']}': {e}")
        summary = "Summary unavailable. Please read the full article at the link below."

    # Return the article dict with 'content' replaced by 'summary'
    # Downstream layers (digest_builder) only need 'summary', not raw content
    return {
        "topic":   article["topic"],
        "title":   article["title"],
        "url":     article["url"],
        "summary": summary,
        "source":  article["source"],
    }


# ---------------------------------------------------------------------------
# BATCH ORCHESTRATION
# ---------------------------------------------------------------------------

async def summarize_all_async(articles: list[dict]) -> list[dict]:
    """
    Summarize all articles using batched parallel execution.

    Splits articles into batches of BATCH_SIZE, runs each batch
    in parallel via asyncio.gather(), waits between batches to
    respect rate limits.

    Args:
        articles: List of raw article dicts from the search layer

    Returns:
        List of summarized article dicts
    """
    all_summaries = []
    total_batches = (len(articles) + BATCH_SIZE - 1) // BATCH_SIZE

    for i in range(0, len(articles), BATCH_SIZE):
        batch = articles[i : i + BATCH_SIZE]
        batch_num = (i // BATCH_SIZE) + 1

        print(f"[Summarizer] Batch {batch_num}/{total_batches} "
              f"— summarizing {len(batch)} articles in parallel...")

        # asyncio.gather() runs all coroutines in batch concurrently
        # It waits until ALL of them finish before continuing
        # *[...] unpacks the list comprehension into individual arguments
        batch_summaries = await asyncio.gather(
            *[summarize_article(article) for article in batch]
        )

        all_summaries.extend(batch_summaries)

        # Don't sleep after the last batch — no point waiting if we're done
        if i + BATCH_SIZE < len(articles):
            await asyncio.sleep(BATCH_DELAY_SECONDS)

    print(f"[Summarizer] Done. Summarized {len(all_summaries)} articles.")
    return all_summaries


def summarize_all(articles: list[dict]) -> list[dict]:
    """
    Synchronous wrapper around summarize_all_async().

    Why does this exist?
    agent.py is a regular synchronous script. It cannot 'await' directly.
    asyncio.run() creates an event loop, runs our async function inside it,
    and returns the result to the synchronous caller.

    This is the standard pattern for calling async code from sync code.
    """
    return asyncio.run(summarize_all_async(articles))