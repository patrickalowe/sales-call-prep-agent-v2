"""
Core agent logic for the Sales Call Prep Agent.

Runs a four-step workflow per briefing:
  1. plan_approach  -- decide the angle before generating
  2. gather_context -- organize what is known about the company
  3. generate_brief -- produce the full seven-section briefing
  4. review_brief   -- flag weak spots in the output

run_agent() is the main entry point. It runs all four steps and returns
a formatted markdown string ready to save.

Each step is a separate function so they can be read, tested, or swapped
out independently. The gather_context() step uses live web search so the
briefing is grounded in current, sourced information rather than the model's
training knowledge alone.
"""

import sys
import time
from datetime import datetime
from pathlib import Path

import anthropic
from anthropic import Anthropic

from prompts import (
    SYSTEM_PROMPT,
    PLANNING_PROMPT,
    CONTEXT_PROMPT,
    BRIEFING_PROMPT,
    REVIEW_PROMPT,
)

MODEL = "claude-sonnet-4-6"

# Anthropic's server-side web search tool. Claude runs the searches on
# Anthropic's infrastructure and folds the results (with sources) back into
# its answer. max_uses caps how many searches one briefing can trigger. Each
# search also pulls result text into the context as input tokens (and each
# pause/resume re-sends that text), so each extra search adds real cost.
# One focused search keeps the per-briefing spend low for testing.
WEB_SEARCH_TOOL = {"type": "web_search_20260209", "name": "web_search", "max_uses": 1}

# Sonnet 4.6 pricing so each run can report its own estimated cost. Dollars
# per token for text, plus the per-request fee for server-side web search.
_PRICE_INPUT = 3.0 / 1_000_000
_PRICE_OUTPUT = 15.0 / 1_000_000
_PRICE_CACHE_READ = 0.30 / 1_000_000
_PRICE_CACHE_WRITE = 3.75 / 1_000_000
_PRICE_WEB_SEARCH = 0.01  # per search request


def _new_usage():
    return {"input": 0, "output": 0, "cache_read": 0, "cache_write": 0, "searches": 0}


def _record_usage(acc, u):
    """Add one response's usage into the running accumulator."""
    if acc is None or u is None:
        return
    acc["input"] += getattr(u, "input_tokens", 0) or 0
    acc["output"] += getattr(u, "output_tokens", 0) or 0
    acc["cache_read"] += getattr(u, "cache_read_input_tokens", 0) or 0
    acc["cache_write"] += getattr(u, "cache_creation_input_tokens", 0) or 0
    server = getattr(u, "server_tool_use", None)
    if server is not None:
        acc["searches"] += getattr(server, "web_search_requests", 0) or 0


def _estimate_cost(acc):
    return (
        acc["input"] * _PRICE_INPUT
        + acc["output"] * _PRICE_OUTPUT
        + acc["cache_read"] * _PRICE_CACHE_READ
        + acc["cache_write"] * _PRICE_CACHE_WRITE
        + acc["searches"] * _PRICE_WEB_SEARCH
    )

# Safety cap on the server-side tool loop, so a runaway search session can't
# spin forever. Each pause_turn is one resume.
_MAX_SEARCH_RESUMES = 8

# How many times to wait out a rate limit (429) before giving up. The search
# step can push input tokens past an entry-tier per-minute cap; waiting for the
# rolling window to reset lets the run finish instead of failing outright.
_MAX_RATE_LIMIT_WAITS = 6
_DEFAULT_RATE_LIMIT_WAIT = 60  # seconds, used when the API sends no retry-after


def _create_with_retry(client, **kwargs):
    """Call messages.create, waiting out rate limits instead of failing.

    On a 429 we honor the API's retry-after header when present, otherwise
    wait a full minute (the per-minute token window) and try again. A short
    notice goes to stderr so a long wait does not look like a hang.
    """
    for attempt in range(_MAX_RATE_LIMIT_WAITS + 1):
        try:
            return client.messages.create(**kwargs)
        except anthropic.RateLimitError as e:
            if attempt >= _MAX_RATE_LIMIT_WAITS:
                raise
            retry_after = e.response.headers.get("retry-after") if e.response else None
            wait = int(retry_after) if retry_after and retry_after.isdigit() else _DEFAULT_RATE_LIMIT_WAIT
            print(
                f"  (rate limit reached; waiting {wait}s for your per-minute "
                f"window to reset, then continuing...)",
                file=sys.stderr,
                flush=True,
            )
            time.sleep(wait)


def _call(client, prompt, max_tokens, tools=None, usage=None):
    """Make an API call and return the combined text response.

    When `tools` includes the web search tool, Claude may pause mid-turn to run
    searches (stop_reason == "pause_turn"); we resume until it finishes. The
    response can contain several blocks (search calls, results, text), so we
    join every text block rather than reading only the first. Token/search
    usage from every response (including resumes) is added to `usage`.
    """
    messages = [{"role": "user", "content": prompt}]

    for _ in range(_MAX_SEARCH_RESUMES + 1):
        kwargs = {
            "model": MODEL,
            "max_tokens": max_tokens,
            "system": SYSTEM_PROMPT,
            "messages": messages,
        }
        if tools:
            kwargs["tools"] = tools

        response = _create_with_retry(client, **kwargs)
        _record_usage(usage, response.usage)

        if response.stop_reason == "pause_turn":
            # Server-side search loop hit its iteration limit. Append what we
            # have and re-send; the API resumes the search automatically.
            messages.append({"role": "assistant", "content": response.content})
            continue
        break

    return "".join(b.text for b in response.content if b.type == "text").strip()


def plan_approach(client, company_name, persona_title, notes, usage=None):
    """Step 1: Plan the angle before generating the brief."""
    prompt = PLANNING_PROMPT.format(
        company_name=company_name,
        persona_title=persona_title,
        notes=notes or "None provided.",
    )
    return _call(client, prompt, max_tokens=400, usage=usage)


def gather_context(client, company_name, persona_title, plan, use_search=True, usage=None):
    """Step 2: Research the company and persona.

    With use_search=True this grounds the brief in current reality (recent
    news, funding, leadership) via live web search. With use_search=False it
    falls back to the model's training knowledge only, which is faster and
    much cheaper, for quick test runs.
    """
    prompt = CONTEXT_PROMPT.format(
        company_name=company_name,
        persona_title=persona_title,
        plan=plan,
    )
    tools = [WEB_SEARCH_TOOL] if use_search else None
    return _call(client, prompt, max_tokens=1000, tools=tools, usage=usage)


def generate_brief(client, company_name, persona_title, notes, plan, context, usage=None):
    """Step 3: Generate the full seven-section briefing."""
    prompt = BRIEFING_PROMPT.format(
        company_name=company_name,
        persona_title=persona_title,
        notes=notes or "None provided.",
        plan=plan,
        context=context,
    )
    return _call(client, prompt, max_tokens=2000, usage=usage)


def review_brief(client, brief, usage=None):
    """Step 4: Flag weak spots in the generated output."""
    prompt = REVIEW_PROMPT.format(brief=brief)
    return _call(client, prompt, max_tokens=400, usage=usage)


def format_output(company_name, persona_title, brief, review):
    """Assemble the final markdown document with metadata and review notes."""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
    return f"""# Sales Call Brief

**Company:** {company_name}
**Persona:** {persona_title}
**Generated:** {timestamp}

---

{brief}

---

## Agent Review Notes

{review}
"""


def save_output(content, company):
    """Save a finished brief to output/ as a timestamped markdown file.

    Shared by both the CLI (main.py) and the web app (app.py) so a briefing
    is saved the same way no matter which one generated it. Returns the path.
    """
    output_dir = Path("output")
    output_dir.mkdir(exist_ok=True)
    slug = company.lower().replace(" ", "_").replace("/", "_").replace(".", "")
    timestamp = datetime.now().strftime("%Y%m%d_%H%M")
    filepath = output_dir / f"{slug}_{timestamp}.md"
    filepath.write_text(content, encoding="utf-8")
    return filepath


def run_agent(company_name, persona_title, notes="", on_step=None, use_search=True):
    """
    Run the full four-step agent workflow and return formatted markdown.

    on_step is an optional callback that receives a status string at each step.
    main.py uses it to print progress without this module knowing about the UI.

    use_search toggles live web search in the context step. True (default)
    grounds the brief in current information; False is the cheaper, faster
    training-knowledge-only path for quick test runs. The final on_step message
    reports token usage and an estimated dollar cost for the run.
    """
    def step(msg):
        if on_step:
            on_step(msg)

    # max_retries=0: we own rate-limit handling in _create_with_retry, where the
    # wait is sized to the per-minute window rather than the SDK's short backoff.
    client = Anthropic(max_retries=0)
    usage = _new_usage()

    step("Planning approach...")
    plan = plan_approach(client, company_name, persona_title, notes, usage=usage)

    step("Researching company (live web search)..." if use_search
         else "Gathering context (no search, training data only)...")
    context = gather_context(client, company_name, persona_title, plan,
                             use_search=use_search, usage=usage)

    step("Generating briefing...")
    brief = generate_brief(client, company_name, persona_title, notes, plan, context, usage=usage)

    step("Running self-check...")
    review = review_brief(client, brief, usage=usage)

    cost = _estimate_cost(usage)
    step(f"Usage: {usage['input']:,} in + {usage['output']:,} out tokens, "
         f"{usage['searches']} search(es) -> est. ${cost:.3f}")

    return format_output(company_name, persona_title, brief, review)
